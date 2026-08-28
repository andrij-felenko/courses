// bordercost.cpp — ціна перетину межі ядра на цій машині (C++20).
//
//   g++ -O2 -Wall -Wextra -std=c++20 -o bordercost bordercost.cpp
//   taskset -c 3 ./bordercost 3

#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <numeric>
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <ctime>
#include <unistd.h>
#include <sched.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <x86intrin.h>

constexpr std::size_t PAGE = 4096;
constexpr int STEPS = 64;
constexpr std::size_t MAX_KIB = 262144;

static inline uint64_t tsc_open()
{
    _mm_lfence();
    uint64_t t = __rdtsc();
    _mm_lfence();
    return t;
}

static inline uint64_t tsc_close()
{
    unsigned aux;
    uint64_t t = __rdtscp(&aux);
    _mm_lfence();
    return t;
}

static double tsc_hz()
{
    struct timespec a{}, b{}, nap{ 0, 200 * 1000 * 1000 };
    clock_gettime(CLOCK_MONOTONIC, &a);
    uint64_t c0 = tsc_open();
    while (nanosleep(&nap, &nap) == -1 && errno == EINTR)
        ;
    uint64_t c1 = tsc_close();
    clock_gettime(CLOCK_MONOTONIC, &b);

    double ns = static_cast<double>(b.tv_sec - a.tv_sec) * 1e9
              + static_cast<double>(b.tv_nsec - a.tv_nsec);
    return static_cast<double>(c1 - c0) * 1e9 / ns;
}
