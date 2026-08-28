/* aspace.cpp — прогулянка власним адресним простором (C++ версія).
 * g++ -O2 -std=c++20 -o aspace aspace.cpp    запуск: ./aspace
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <setjmp.h>
#include <signal.h>
#include <sys/mman.h>
#include <unistd.h>

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <string_view>

constexpr unsigned long MIB = 1024UL * 1024UL;
static unsigned long PAGE = 4096;

static void show(std::string_view what)
{
    unsigned long vsz = 0, rss = 0;
    if (std::ifstream statm{"/proc/self/statm"}) {
        statm >> vsz >> rss;
    }
    std::cout << "VSZ " << std::setw(8) << std::fixed << std::setprecision(1)
              << (static_cast<double>(vsz) * PAGE / MIB) << " МіБ   RSS "
              << std::setw(8) << std::setprecision(2)
              << (static_cast<double>(rss) * PAGE / MIB) << " МіБ ("
              << std::setw(6) << rss << " стор.)   " << what << '\n';
}

static void maps(std::string_view what, const char* lo, const char* hi)
{
    std::cout << "--- /proc/self/maps, " << what << '\n';
    std::ifstream f{"/proc/self/maps"};
    if (!f) return;
    std::string line;
    const auto lo_addr = reinterpret_cast<std::uintptr_t>(lo);
    const auto hi_addr = reinterpret_cast<std::uintptr_t>(hi);
    while (std::getline(f, line)) {
        std::uintptr_t a = 0, b = 0;
        if (std::sscanf(line.c_str(), "%lx-%lx", &a, &b) == 2 &&
            a < hi_addr && b > lo_addr) {
            std::cout << line << '\n';
        }
    }
}
