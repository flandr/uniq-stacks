# Copyright (c) 2015 Nathan Rosenblum
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''
Isolation of unique stack traces (according to various equivalence
criteria) from threads in GDB inferiors.
'''

try:
    import gdb
except ImportError as e:
    raise ImportError("This script must be run in GDB: ", str(e))

class StackTrace(object):
    '''
    A stack trace from a thread
    '''

    class Frame(object):
        '''
        A frame from a stack trace
        '''

        def __init__(self, gdb_frame, position, ignore_pc):
            self.position = position
            self.pc = gdb_frame.pc()
            self.name = gdb_frame.name()
            if self.name is None:
                self.name = "[unknown {:#x}]".format(self.pc)
            self.ignore_pc = ignore_pc
            if gdb_frame.type() == gdb.INLINE_FRAME:
                self.name += " [inlined]"

        def __eq__(self, other):
            ret = self.position == other.position and \
                    self.name == other.name
            if self.ignore_pc:
                return ret
            return ret and self.pc == other.pc

        def __ne__(self, other):
            return not self.__eq__(other)

        def __hash__(self):
            base = hash((self.position, self.name))
            if self.ignore_pc:
                return base
            return hash((base, self.pc))

        def __str__(self):
            if self.ignore_pc:
                return "#{:3d} {}".format(self.position, self.name)
            else:
                return "#{:3d} {:#x} {}".format(self.position, self.pc,
                        self.name)

    @staticmethod
    def accumulate_backtrace(frame, skip_frames, frame_limit, ignore_pc):
        '''
        Performs the backtrace over the selected thread, assembling a list
        of Frame objects
        '''

        i = 0
        frames = []

        while frame and i <= frame_limit:
            if i >= skip_frames:
                frames.append(StackTrace.Frame(frame, i, ignore_pc))

            frame = frame.older()
            i += 1

        return frames

    def __init__(self, gdb_thread, skip_frames, frame_limit, ignore_pc):
        if not gdb_thread.is_valid():
            raise RuntimeError("Invalid thread object")

        self.gdb_thread_id = gdb_thread.num
        (self.pid, self.lwpid, self.tid) = gdb_thread.ptid

        # Preserve previous selected thread (may be None)
        orig_thread = gdb.selected_thread()

        try:
            # Switch to current thread
            gdb_thread.switch()

            # Get the backtrace in its entirety
            self.frames = self.accumulate_backtrace(gdb.newest_frame(),
                skip_frames, frame_limit, ignore_pc)
        finally:
            if orig_thread:
                orig_thread.switch()

    def __eq__(self, other):
        return self.frames == other.frames

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # I know you're trying to protect ourselves from ourselves,
        # Python, but I really do want a hash of this list
        return hash(str([hash(f) for f in self.frames]))

    def __str__(self):
        framestr = [str(f) for f in self.frames]
        return "\n".join(framestr)

