// faultlab.cpp — вимірювання сторінкових збоїв (C++17)
// Збірка: g++ -O2 -std=c++17 -o faultlab faultlab.cpp
#include <iostream>
#include <iomanip>
#include <string>
#include <string_view>
#include <vector>
#include <algorithm>
#include <random>
#include <chrono>
#include <cstring>
#include <cstdio>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/stat.h>

#ifndef MADV_POPULATE_WRITE
#define MADV_POPULATE_WRITE 23
#endif

constexpr std::size_t PGSZ = 4096;
constexpr std::size_t ANON = 1024UL * 1024 * 1024; // 1 GiB
constexpr std::size_t FSIZE = 256UL * 1024 * 1024;  // 256 MiB

static volatile unsigned long sink = 0;

struct mark {
    double t;
    unsigned long minf, majf;
};

static double now() {
    using namespace std::chrono;
    return duration_cast<duration<double>>(steady_clock::now().time_since_epoch()).count();
}

static void counters(unsigned long &minf, unsigned long &majf) {
    struct rusage ru{};
    getrusage(RUSAGE_SELF, &ru);
    minf = ru.ru_minflt;
    majf = ru.ru_majflt;
}

static void mark_begin(mark &m) {
    counters(m.minf, m.majf);
    m.t = now();
}

static void mark_end(const mark &m, std::string_view what) {
    double dt = now() - m.t;
    unsigned long minf, majf;
    counters(minf, majf);
    std::cout << "  " << std::left << std::setw(32) << what
              << std::right << std::setw(9) << std::fixed << std::setprecision(3) << (dt * 1e3) << " мс"
              << "   minflt +" << std::left << std::setw(8) << (minf - m.minf)
              << " majflt +" << (majf - m.majf) << "\n";
}
