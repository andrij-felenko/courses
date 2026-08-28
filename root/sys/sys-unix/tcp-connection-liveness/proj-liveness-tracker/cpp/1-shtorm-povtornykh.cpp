/* Вирахування затримки з випадковим відхиленням (jitter) у C++ */
#include <chrono>
#include <random>
#include <algorithm>

std::chrono::seconds calculate_backoff_cpp(int attempt, std::chrono::seconds base, std::chrono::seconds max_val) {
    auto backoff_count = base.count() * (1LL << attempt);
    auto capped_count = std::min<long long>(backoff_count, max_val.count());
    auto half = capped_count / 2;
    
    thread_local std::mt19937 rng{std::random_device{}()};
    std::uniform_int_distribution<long long> dist(0, half);
    
    return std::chrono::seconds(half + dist(rng));
}
