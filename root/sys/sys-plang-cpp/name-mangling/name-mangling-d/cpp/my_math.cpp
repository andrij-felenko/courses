/* Реалізація my_math.cpp на повноцінному C++ */
#include "my_math.h"
#include <vector>
#include <numeric>

extern "C" int fast_multiply(int a, int b) {
    // Усередині дозволені будь-які конструкції C++
    std::vector<int> factors = {a, b};
    return std::accumulate(factors.begin(), factors.end(), 1, [](int x, int y) {
        return x * y;
    });
}
