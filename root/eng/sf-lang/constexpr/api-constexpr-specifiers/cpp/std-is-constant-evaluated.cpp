#include <type_traits>

constexpr double power(double base, int exp) {
    if (std::is_constant_evaluated()) {
        // Гілка для компілятора: чистий цикл без системних інтринсиків
        double res = 1.0;
        for (int i = 0; i < exp; ++i) res *= base;
        return res;
    } else {
        // Гілка для рантайму: використання апаратних інструкцій процесора
        return __builtin_pow(base, exp);
    }
}
