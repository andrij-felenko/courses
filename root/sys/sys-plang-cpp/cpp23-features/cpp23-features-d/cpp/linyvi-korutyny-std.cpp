#include <generator>
#include <ranges>
#include <print>

std::generator<uint64_t> generate_primes() {
    co_yield 2;
    co_yield 3;
    for (uint64_t n = 5; ; n += 2) {
        bool is_prime = true;
        for (uint64_t i = 3; i * i <= n; i += 2) {
            if (n % i == 0) { is_prime = false; break; }
        }
        if (is_prime) co_yield n;
    }
}

int main() {
    // Об'єднання генератора з адаптерами std::ranges
    for (auto prime : generate_primes() 
                    | std::views::filter([](auto p) { return p % 10 == 7; })
                    | std::views::take(5)) {
        std::println("Просте число: {}", prime);
    }
}
