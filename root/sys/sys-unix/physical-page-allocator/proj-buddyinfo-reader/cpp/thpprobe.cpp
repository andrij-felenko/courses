// thpprobe.cpp — скільки блоків порядку 9 система дасть НАСПРАВДІ.
// Збірка: c++ -O2 -std=c++20 -o thpprobe thpprobe.cpp
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unistd.h>
#include <sys/mman.h>

#ifndef MADV_COLLAPSE
#define MADV_COLLAPSE 25
#endif

static long sysfs_num(const std::string &path)
{
    std::ifstream f(path);
    if (!f) return -1;
    long v = -1;
    f >> v;
    return f ? v : -1;
}

static long vmstat(std::string_view key)
{
    std::ifstream f("/proc/vmstat");
    if (!f) return -1;
    std::string line;
    while (std::getline(f, line)) {
        if (line.starts_with(key) && line.size() > key.size() && line[key.size()] == ' ') {
            return std::stol(line.substr(key.size() + 1));
        }
    }
    return -1;
}

static long anon_thp_kb()
{
    std::ifstream f("/proc/self/smaps_rollup");
    if (!f) return -1;
    std::string line;
    while (std::getline(f, line)) {
        if (line.starts_with("AnonHugePages:")) {
            return std::stol(line.substr(14));
        }
    }
    return -1;
}

static double now_us()
{
    auto now = std::chrono::steady_clock::now();
    return std::chrono::duration<double, std::micro>(now.time_since_epoch()).count();
}
