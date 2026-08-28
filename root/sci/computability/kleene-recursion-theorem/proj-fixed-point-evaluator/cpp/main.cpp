#include <iostream>
#include <functional>
#include <utility>
#include <vector>
#include <unordered_map>
#include <cstdint>

// Універсальний фіксатор нерухомої точки для C++ (Z-комбінатор)
template <typename F>
class FixedPoint {
    F func;

public:
    constexpr explicit FixedPoint(F&& f) : func(std::forward<F>(f)) {}
    constexpr explicit FixedPoint(const F& f) : func(f) {}

    template <typename... Args>
    constexpr decltype(auto) operator()(Args&&... args) const {
        // Передаємо *this як перший аргумент lambda-функції (self-reference)
        return func(*this, std::forward<Args>(args)...);
    }
};

// Фабрична функція створення об'єкта нерухомої точки
template <typename F>
constexpr auto make_fixed(F&& f) {
    return FixedPoint<std::decay_t<F>>(std::forward<F>(f));
}

// Декоратор мемоізації над оператором нерухомої точки
template <typename F>
auto make_memoized_fixed(F&& f) {
    auto memo = std::make_shared<std::unordered_map<uint64_t, uint64_t>>();
    return make_fixed([f = std::forward<F>(f), memo](const auto& self, uint64_t n) -> uint64_t {
        auto it = memo->find(n);
        if (it != memo->end()) {
            return it->second;
        }
        uint64_t val = f(self, n);
        (*memo)[n] = val;
        return val;
    });
}

int main() {
    // Анонімний функціонал факторіалу
    auto factorial = make_fixed([](const auto& self, uint64_t n) -> uint64_t {
        return (n == 0) ? 1 : n * self(n - 1);
    });

    // Мемоізований функціонал чисел Фібоначчі: знижує складність з O(2^n) до O(n)
    auto fibonacci = make_memoized_fixed([](const auto& self, uint64_t n) -> uint64_t {
        if (n == 0) return 0;
        if (n == 1) return 1;
        return self(n - 1) + self(n - 2);
    });

    // Двомісна функція Аккермана без глобального імені
    auto ackermann = make_fixed([](const auto& self, uint64_t m, uint64_t n) -> uint64_t {
        if (m == 0) return n + 1;
        if (n == 0) return self(m - 1, 1);
        return self(m - 1, self(m, n - 1));
    });

    constexpr uint64_t n = 10;
    std::cout << "Факторіал " << n << " = " << factorial(n) << '\n';
    std::cout << "Фібоначчі " << n << " = " << fibonacci(n) << '\n';
    std::cout << "Аккерман(3, 2) = " << ackermann(3, 2) << '\n';

    return 0;
}
