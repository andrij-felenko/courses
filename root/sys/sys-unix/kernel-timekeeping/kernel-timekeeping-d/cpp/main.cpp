#include <chrono>
#include <print>

void do_work();

void measure()
{
    // steady_clock у libstdc++ — це саме CLOCK_MONOTONIC;
    // system_clock — CLOCK_REALTIME, і для тривалостей не годиться.
    const auto t0 = std::chrono::steady_clock::now();
    do_work();
    const auto t1 = std::chrono::steady_clock::now();

    std::println("{}", std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0));
}
