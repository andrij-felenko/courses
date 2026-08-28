// my_math.cpp — Реалізація мовою C++
#include "my_math.hpp"

namespace math {
    int add(int a, int b) noexcept {
        return a + b;
    }

    int square(int x) noexcept {
        return x * x;
    }
}
