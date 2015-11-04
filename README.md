# Finding unique stack traces in GDB

When debugging multi-threaded applications, it's easy to get lost in a forest
of similar stack traces and to miss out on the one that slightly differs. This
is especially trying when using thread pools or other code patterns in which
many threads are waiting about on condition variable with similar calling
histories.

This project adds a `uniq-stacks` command to GDB that can help find equivalence
classes for stack traces. It works like so:

```
(gdb)

== Printing 3 unique stacks from 7 threads

Stack for thread ids [3, 2, 1]
#  0 0x7ffff739df3d nanosleep
#  1 0x7ffff739ddd4 __sleep
#  2 0x400d5c __lambda1::operator()
#  3 0x402aa8 std::_Bind_simple<main(int, char**)::__lambda1()>::_M_invoke<>(std::_Index_tuple<>)
#  4 0x402997 std::_Bind_simple<main(int, char**)::__lambda1()>::operator()(void)
#  5 0x4028c8 std::thread::_Impl<std::_Bind_simple<main(int, char**)::__lambda1()> >::_M_run(void)
#  6 0x7ffff7b87a40 [unknown 0x7ffff7b87a40]
#  7 0x7ffff76aa182 start_thread
#  8 0x7ffff73d747d clone

Stack for thread ids [6, 5, 4]
#  0 0x7ffff739df3d nanosleep
#  1 0x7ffff739ddd4 __sleep
#  2 0x400d44 __lambda0::operator()
#  3 0x402b06 std::_Bind_simple<main(int, char**)::__lambda0()>::_M_invoke<>(std::_Index_tuple<>)
#  4 0x4029b5 std::_Bind_simple<main(int, char**)::__lambda0()>::operator()(void)
#  5 0x4028e6 std::thread::_Impl<std::_Bind_simple<main(int, char**)::__lambda0()> >::_M_run(void)
#  6 0x7ffff7b87a40 [unknown 0x7ffff7b87a40]
#  7 0x7ffff76aa182 start_thread
#  8 0x7ffff73d747d clone

Stack for thread ids [7]
#  0 0x7ffff76ab66b pthread_join
#  1 0x7ffff7b87837 std::thread::join()
#  2 0x400df5 main
```

You can reduce the number of stack frames that are considered with an optional
parameter:

```
(gdb) uniq-stacks 4

== Printing 3 unique stacks from 7 threads

Stack for thread ids [4, 3, 2]
#  0 0x7f5669cd8f3d nanosleep
#  1 0x7f5669cd8dd4 __sleep
#  2 0x400d5c __lambda1::operator()
#  3 0x402aa8 std::_Bind_simple<main(int, char**)::__lambda1()>::_M_invoke<>(std::_Index_tuple<>)
#  4 0x402997 std::_Bind_simple<main(int, char**)::__lambda1()>::operator()(void)

Stack for thread ids [7, 6, 5]
#  0 0x7f5669cd8f3d nanosleep
#  1 0x7f5669cd8dd4 __sleep
#  2 0x400d44 __lambda0::operator()
#  3 0x402b06 std::_Bind_simple<main(int, char**)::__lambda0()>::_M_invoke<>(std::_Index_tuple<>)
#  4 0x4029b5 std::_Bind_simple<main(int, char**)::__lambda0()>::operator()(void)

Stack for thread ids [1]
#  0 0x7f5669fe666b pthread_join
#  1 0x7f566a4c2837 std::thread::join()
#  2 0x400df5 main

```

There are other options; run `uniq-stacks --help` for more details.

## Installing and using in GDB

You have two options:

 1. Copy `uniq-stacks.py` and `lib` into GDB's data directory (see `show
    data-directory`) in `${data-directory}/python/gdb/command`

 2. Source the script on startup like `source ${path}/uniq-stacks.py`

## License

Copyright © 2015 Nathan Rosenblum flander@gmail.com

Licensed under the MIT License.

## References

Inspired by the
[uniqstack](https://msdn.microsoft.com/en-us/library/windows/hardware/ff565548(v=vs.85).aspx)
command in WinDbg.

