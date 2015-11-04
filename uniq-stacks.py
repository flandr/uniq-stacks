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
Implements GDB entrypoint for 'uniq-stacks' command

example usage:
    (gdb) source uniq-stacks.py
    (gdb) uniq-stacks

'''

try:
    import gdb
except ImportError as e:
    raise ImportError("This script must be run in GDB: ", str(e))

import argparse
import os
import sys

# Fix up imports
abspath = os.path.abspath(__file__)
sys.path.append(os.path.dirname(abspath))

import lib.stacks as stacks

class UniqStacksCommand(gdb.Command):
    '''
    A GDB command that prints unique stack frames in the inferior process.

    This command is intended to help simplify debugging, particularly core
    dump analysis, for heavily multithreaded programs.

    Type uniq-stacks -h for options.
    '''

    _command = "uniq-stacks"

    def __init__(self):
        gdb.Command.__init__(self, self._command, gdb.COMMAND_STACK)

    class NoexitArgumentParser(argparse.ArgumentParser):
        def exit(self, status=0, message=None):
            if status != 0:
                # Non-zero exit
                raise gdb.GdbError(message)
            # Silent
            raise gdb.GdbError(" ")

    def invoke(self, argument, from_tty):
        parser = self.NoexitArgumentParser(prog=self._command,
                description=self.__doc__)
        parser.add_argument('limit', metavar='limit', type=int, nargs='?',
                default=sys.maxsize, help='Only consider [limit] stack frames')
        parser.add_argument('--skip', metavar='N', nargs='?', type=int,
                default=0, help='Skip first [N] stack frames')
        parser.add_argument('--ignore-pc', action='store_true', default=False,
                help='Ignore program counter for frame equivalence')

        args = parser.parse_args(gdb.string_to_argv(argument))

        traces = []
        for thread in gdb.inferiors()[0].threads():
            traces.append(stacks.StackTrace(thread, args.skip, args.limit,
                args.ignore_pc))

        uniq = {}
        for stack in traces:
            uniq.setdefault(stack,[]).append(stack.gdb_thread_id)

        sorter = lambda d: sorted(d.items(), key=lambda item: len(item[1]),
                reverse=True)

        gdb.write("\n== Printing {} unique stacks from {} threads\n\n".format(
            len(uniq), len(traces)))

        for k, v in sorter(uniq):
            gdb.write("Stack for thread ids {}\n".format(sorted(v)))
            gdb.write(str(k))
            gdb.write("\n\n")

        gdb.flush()

UniqStacksCommand()
