#include <algorithm>
#include <execution>
#include <vector>

std::vector<int> large_dataset(10'000'000);

// 1. Послідовне виконання (класичне):
std::sort(std::execution::seq, large_dataset.begin(), large_dataset.end());

// 2. Паралельне виконання на пулі потоків процесора:
std::sort(std::execution::par, large_dataset.begin(), large_dataset.end());

// 3. Паралельне та векторизоване виконання (SIMD):
std::sort(std::execution::par_unseq, large_dataset.begin(), large_dataset.end());
