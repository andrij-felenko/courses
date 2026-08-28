// src/calc.cpp — обчислювальний модуль ідіоматичною мовою C++
#include <iostream>
#include <numeric>
#include <vector>
#include <ranges>

constexpr long long compute_factorial(int n) noexcept {
    if (n <= 1) return 1;
    long long result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

int main() {
    constexpr int val = 10;
    std::cout << "Факторіал " << val << " = " 
              << compute_factorial(val) << '\n';
    return 0;
}
