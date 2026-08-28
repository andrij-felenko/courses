#include <iostream>
#include <vector>
#include <cstdint>

// Безпечне модульне піднесення до степеня (base^exp % mod)
uint64_t power_mod(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            // Використовуємо __int128 для уникнення переповнення при множенні
            res = static_cast<uint64_t>((static_cast<__int128>(res) * base) % mod);
        }
        base = static_cast<uint64_t>((static_cast<__int128>(base) * base) % mod);
        exp /= 2;
    }
    return res;
}

// Детермінований тест Міллера-Рабіна для uint64_t
bool is_prime(uint64_t n) {
    if (n < 2) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0) return false;

    // Представляємо n - 1 як d * 2^s
    uint64_t d = n - 1;
    int s = 0;
    while (d % 2 == 0) {
        d /= 2;
        s++;
    }

    // Детерміновані бази, достатні для будь-якого uint64_t
    std::vector<uint64_t> bases = {2, 325, 9375, 28178, 450775, 9780504, 1795265022};

    for (uint64_t a : bases) {
        // Якщо база кратна числу n, ігноруємо її
        if (a % n == 0) continue;

        uint64_t x = power_mod(a, d, n);
        if (x == 1 || x == n - 1) continue;

        bool composite = true;
        for (int r = 1; r < s; r++) {
            x = static_cast<uint64_t>((static_cast<__int128>(x) * x) % n);
            if (x == n - 1) {
                composite = false;
                break;
            }
        }
        
        // Якщо жодна умова не виконалася, число гарантовано складене
        if (composite) return false;
    }
    return true;
}

int main() {
    std::vector<uint64_t> test_nums = {97, 1000000007, 4294967291, 18446744073709551557ULL};
    for (uint64_t n : test_nums) {
        std::cout << n << " is " << (is_prime(n) ? "prime" : "composite") << "\n";
    }
    return 0;
}
