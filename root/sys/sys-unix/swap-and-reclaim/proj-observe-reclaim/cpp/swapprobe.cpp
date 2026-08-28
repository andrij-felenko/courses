// swapprobe.cpp — витіснити власну ділянку й виміряти ціну її повернення в C++20
// збірка: g++ -O2 -std=c++20 -Wall -Wextra -o swapprobe_cpp swapprobe.cpp
// запуск: ./swapprobe_cpp [МіБ] [r|w]
#define _GNU_SOURCE
#include <iostream>
#include <iomanip>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <ctime>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/resource.h>

#ifndef MADV_COLD
#define MADV_COLD     20
#endif
#ifndef MADV_PAGEOUT
#define MADV_PAGEOUT  21
#endif

namespace {

long page_size() {
    static const long ps = sysconf(_SC_PAGESIZE);
    return ps;
}

size_t count_resident_pages(void* addr, size_t len) {
    const size_t pages = len / static_cast<size_t>(page_size());
    std::vector<unsigned char> vec(pages);
    if (mincore(addr, len, vec.data()) != 0) {
        std::perror("mincore");
        std::exit(1);
    }
    size_t live = 0;
    for (auto b : vec) {
        if (b & 1u) ++live;
    }
    return live;
}

long read_status_kb(const std::string& key) {
    std::ifstream file("/proc/self/status");
    if (!file) return -1;
    std::string line;
    while (std::getline(file, line)) {
        if (line.rfind(key + ":", 0) == 0) {
            size_t pos = line.find_first_of("0123456789");
            if (pos != std::string::npos) {
                return std::stol(line.substr(pos));
            }
        }
    }
    return -1;
}

long get_major_faults() {
    struct rusage ru{};
    getrusage(RUSAGE_SELF, &ru);
    return ru.ru_majflt;
}

void touch_memory(void* addr, size_t len, bool write_mode) {
    volatile auto* p = static_cast<volatile unsigned char*>(addr);
    const size_t ps = static_cast<size_t>(page_size());
    unsigned sink = 0;
    for (size_t i = 0; i < len; i += ps) {
        if (write_mode) {
            p[i] = 1;
        } else {
            sink += p[i];
        }
    }
    (void)sink;
}

void print_snapshot(const char* label, void* addr, size_t len) {
    std::cout << label << "\n"
              << "   резидентних " << count_resident_pages(addr, len)
              << " з " << (len / static_cast<size_t>(page_size()))
              << "   RssAnon " << read_status_kb("RssAnon") << " кБ"
              << "   VmSwap " << read_status_kb("VmSwap") << " кБ"
              << "   majflt " << get_major_faults() << "\n";
}

size_t settle_reclaim(void* addr, size_t len, int max_ms) {
    using namespace std::chrono;
    auto deadline = steady_clock::now() + milliseconds(max_ms);
    size_t prev = count_resident_pages(addr, len);
    while (steady_clock::now() < deadline) {
        struct timespec ts{0, 20 * 1000 * 1000};
        nanosleep(&ts, nullptr);
        size_t cur = count_resident_pages(addr, len);
        if (cur == 0 || cur == prev) return cur;
        prev = cur;
    }
    return count_resident_pages(addr, len);
}

bool has_swap() {
    std::ifstream file("/proc/swaps");
    if (!file) return false;
    std::string line;
    size_t lines = 0;
    while (std::getline(file, line)) ++lines;
    return lines > 1;
}

} // namespace

int main(int argc, char** argv) {
    size_t mib = (argc > 1) ? std::stoul(argv[1]) : 256;
    bool wmode = (argc > 2 && argv[2][0] == 'w');
    if (mib == 0) {
        std::cerr << "розмір має бути більший за нуль\n";
        return 2;
    }
    size_t len = mib * 1024 * 1024;
    size_t pages = len / static_cast<size_t>(page_size());

    if (!has_swap()) {
        std::cerr << "УВАГА: жодної області свопу — анонімним сторінкам "
                     "нікуди йти, витіснення не станеться\n";
    }

    void* a = mmap(nullptr, len, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (a == MAP_FAILED) {
        std::perror("mmap");
        return 1;
    }

    if (madvise(a, len, MADV_NOHUGEPAGE) != 0) {
        std::cerr << "MADV_NOHUGEPAGE: " << std::strerror(errno)
                  << " — числа будуть грубіші\n";
    }

    print_snapshot("1 щойно виділено", a, len);

    touch_memory(a, len, true);
    print_snapshot("2 після торкання", a, len);

    if (madvise(a, len, MADV_PAGEOUT) != 0) {
        std::cerr << "MADV_PAGEOUT: " << std::strerror(errno)
                  << " (потрібен Linux 5.4+)\n";
        munmap(a, len);
        return 1;
    }
    size_t left = settle_reclaim(a, len, 5000);
    if (left > 0) {
        std::cerr << "лишилося резидентними " << left << " сторінок: "
                     "MADV_PAGEOUT — підказка, а не наказ\n";
    }
    print_snapshot("3 після MADV_PAGEOUT", a, len);

    long mf0 = get_major_faults();
    auto t0 = std::chrono::steady_clock::now();
    touch_memory(a, len, wmode);
    auto t1 = std::chrono::steady_clock::now();
    long mf1 = get_major_faults();

    print_snapshot("4 після повернення", a, len);

    double us = std::chrono::duration<double, std::micro>(t1 - t0).count();
    std::cout << std::fixed << std::setprecision(1);
    std::cout << "\nповернення " << pages << " сторінок (" << mib << " МіБ) "
              << (wmode ? "записом" : "читанням") << "\n"
              << "  великих збоїв   " << (mf1 - mf0) << " ("
              << (100.0 * static_cast<double>(mf1 - mf0) / static_cast<double>(pages)) << " % сторінок)\n"
              << "  час             " << (us / 1000.0) << " мс\n"
              << "  на сторінку     " << (us / static_cast<double>(pages)) << " мкс\n";
    if (mf1 > mf0) {
        std::cout << "  на великий збій " << (us / static_cast<double>(mf1 - mf0)) << " мкс\n";
    }

    munmap(a, len);
    return 0;
}
