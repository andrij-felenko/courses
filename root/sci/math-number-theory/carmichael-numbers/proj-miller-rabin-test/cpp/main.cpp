#include <iostream>
#include <vector>
#include <cstdint>

// Функція для безпечного множення (a * b) % m без переповнення 64-бітних чисел
uint64_t multiply(uint64_t a, uint64_t b, uint64_t m) {
    uint64_t result = 0;
    a %= m;
    while (b > 0) {
        if (b % 2 == 1) result = (result + a) % m;
        a = (a * 2) % m;
        b /= 2;
    }
    return result;
}

// Функція для швидкого піднесення до степеня (base^exp) % mod
uint64_t power(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) result = multiply(result, base, mod);
        base = multiply(base, base, mod);
        exp /= 2;
    }
    return result;
}

// [Тест Міллера — Рабіна](root:math-number-theory/miller-rabin-test)
bool isPrime(uint64_t n) {
    if (n < 2) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0) return false;

    // Представляємо n-1 у вигляді d * 2^r
    uint64_t d = n - 1;
    int r = 0;
    while (d % 2 == 0) {
        d /= 2;
        r++;
    }

    // Набір баз для детермінованої перевірки чисел до 2^64
    std::vector<uint64_t> bases = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};

    for (uint64_t a : bases) {
        if (n <= a) break;
        
        uint64_t x = power(a, d, n);
        if (x == 1 || x == n - 1) continue;

        bool composite = true;
        for (int i = 1; i < r; i++) {
            x = multiply(x, x, n);
            if (x == n - 1) {
                composite = false;
                break;
            }
        }
        if (composite) return false;
    }
    return true;
}

int main() {
    // 561, 1105 - відомі числа Кармайкла
    uint64_t numbers[] = {17, 561, 1105, 9999999900000001ULL, 2305843009213693951ULL};
    
    for (uint64_t num : numbers) {
        std::cout << num << " is " << (isPrime(num) ? "Prime" : "Composite") << "\n";
    }
    
    return 0;
}
