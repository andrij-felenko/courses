#include <iostream>
#include <vector>
#include <numeric>
#include <random>
#include <algorithm>

using u64 = uint64_t;
using u128 = __uint128_t;

// Швидке модульне піднесення до степеня a^b mod m
u64 power(u64 base, u64 exp, u64 mod) {
    u64 res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (u128)res * base % mod;
        base = (u128)base * base % mod;
        exp /= 2;
    }
    return res;
}

// Імовірнісний [Тест Міллера — Рабіна](root:math-number-theory/miller-rabin-test) на простоту
bool is_prime(u64 n) {
    if (n < 2) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0) return false;

    u64 d = n - 1;
    int s = 0;
    while (d % 2 == 0) {
        d /= 2;
        s++;
    }

    // Бази, достатні для перевірки всіх 64-бітних чисел
    static const u64 bases[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    for (u64 a : bases) {
        if (n <= a) break;
        u64 x = power(a, d, n);
        if (x == 1 || x == n - 1) continue;
        bool composite = true;
        for (int r = 1; r < s; r++) {
            x = (u128)x * x % n;
            if (x == n - 1) {
                composite = false;
                break;
            }
        }
        if (composite) return false;
    }
    return true;
}

// Ро-метод Полларда для пошуку одного дільника
u64 pollard_rho(u64 n) {
    if (n % 2 == 0) return 2;
    if (is_prime(n)) return n;
    
    std::mt19937_64 gen(1337);
    std::uniform_int_distribution<u64> dist(2, n - 1);
    
    u64 x = dist(gen);
    u64 y = x;
    u64 c = dist(gen);
    u64 d = 1;
    
    auto f = [&](u64 val) {
        return ((u128)val * val + c) % n;
    };
    
    while (d == 1) {
        x = f(x);
        y = f(f(y));
        u64 diff = x > y ? x - y : y - x;
        d = std::gcd(diff, n);
        if (d == n) return pollard_rho(n); // повторний запуск з новими x, c
    }
    return d;
}

// Рекурсивна факторизація до простих множників
void factorize(u64 n, std::vector<u64>& factors) {
    if (n == 1) return;
    if (is_prime(n)) {
        factors.push_back(n);
        return;
    }
    u64 divisor = pollard_rho(n);
    factorize(divisor, factors);
    factorize(n / divisor, factors);
}

int main() {
    u64 n = 13835058055282163712ull; // Велике тестове число
    std::cout << "Факторизація числа " << n << ":\n";
    
    std::vector<u64> factors;
    factorize(n, factors);
    std::sort(factors.begin(), factors.end());
    
    for (size_t i = 0; i < factors.size(); ++i) {
        std::cout << factors[i] << (i + 1 == factors.size() ? "" : " * ");
    }
    std::cout << "\n";
    
    return 0;
}
