// limits.hpp
struct Limits {
    static constexpr int max_users = 128;   // оголошення і водночас ініціалізатор
};

// session.cpp
#include <algorithm>
#include "limits.hpp"

int clamp_users(int n) {
    if (n <= Limits::max_users)             // просто читаємо значення — не odr-use
        return n;
    return std::min(n, Limits::max_users);  // параметр std::min — const int&
}
