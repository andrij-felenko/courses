// cleaner.cpp — імітований лог-структурований том на C++20.
// Збірка: g++ -std=c++20 -O2 -o cleaner cleaner.cpp
#include <iostream>
#include <vector>
#include <array>
#include <cstdint>
#include <iomanip>
#include <algorithm>

constexpr std::size_t SEG_BLOCKS  = 64;   // слотів у сегменті
constexpr std::size_t NSEGS       = 512;  // сегментів на томі
constexpr std::size_t FILE_BLOCKS = 64;   // блоків у файлі
constexpr std::int64_t WARMUP     = 100000L;
constexpr std::size_t MEASURE    = 200000L;

constexpr std::int32_t LOW_FREE   = 8;    // поріг увімкнення прибирача
constexpr std::int32_t RESERVE    = 4;    // резерв лише для прибирача

enum class Policy { Greedy, CostBenefit };

struct SummaryEntry {
    std::int32_t ino{-1};
    std::int32_t off{-1};
};

struct Segment {
    std::array<SummaryEntry, SEG_BLOCKS> sum{};
    std::int32_t written{0};
    std::int32_t live{0};
    std::uint64_t sealed{0};
    bool is_free{true};
};

struct LogVolumeState {
    std::array<Segment, NSEGS> seg{};
    std::vector<std::array<std::int32_t, FILE_BLOCKS>> inode{};
    std::int32_t nfiles{0};
    std::int32_t nhot{0};
    std::int32_t free_segs{static_cast<std::int32_t>(NSEGS)};
    std::array<std::int32_t, 2> head{-1, -1};
    std::uint64_t now_{0};
    Policy policy{Policy::Greedy};
    bool sep_head{true};

    std::int64_t user_writes{0};
    std::int64_t clean_writes{0};
    std::int64_t clean_reads{0};
    std::int64_t victims{0};
    std::int64_t stalls{0};
    double u_sum{0.0};
};

static LogVolumeState state;
