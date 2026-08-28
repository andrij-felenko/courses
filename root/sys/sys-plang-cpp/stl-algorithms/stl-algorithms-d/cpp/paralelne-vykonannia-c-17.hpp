#include <algorithm>
#include <execution>

std::vector<double> data(10'000'000);

// Послідовне сортування
std::sort(std::execution::seq, data.begin(), data.end());

// Паралельне багатопоточне сортування
std::sort(std::execution::par, data.begin(), data.end());

// Паралельне та векторизоване (SIMD) сортування
std::sort(std::execution::par_unseq, data.begin(), data.end());
