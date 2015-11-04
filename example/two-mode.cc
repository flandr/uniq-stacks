#include <stdio.h>
#include <unistd.h>

#include <thread>

template<typename Func>
void common2(Func f) {
    f();
}

template<typename Func>
void common1(Func f) {
    common2(f);
}

int main(int argc, char **argv) {
    auto t1 = []() -> void { while (true) { sleep(1); } };
    auto t2 = []() -> void { while (true) { sleep(1); } };

    auto w1 = std::thread(t1);
    auto w2 = std::thread(t1);
    auto w3 = std::thread(t1);

    auto w4 = std::thread(t2);
    auto w5 = std::thread(t2);
    auto w6 = std::thread(t2);

    w1.join();

    return 0;
}
