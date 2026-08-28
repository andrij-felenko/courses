#include <iostream>
#include <vector>
#include <cstdint>
#include <cmath>
#include <omp.h>

// Модулярне множення (a * b) % mod з захистом від переповнення 64-бітних цілих
static inline std::uint64_t mul_mod(std::uint64_t a, std::uint64_t b, std::uint64_t mod) {
    #if defined(__SIZEOF_INT128__)
    return static_cast<std::uint64_t>((static_cast<unsigned __int128>(a) * b) % mod);
    #else
    std::uint64_t res = 0;
    a %= mod;
    while (b > 0) {
        if (b & 1) res = (res + a) % mod;
        a = (a * 2) % mod;
        b >>= 1;
    }
    return res;
    #endif
}

// Модулярне піднесення до степеня (base^exp) % mod
static std::uint64_t power_mod(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) {
    std::uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) res = mul_mod(res, base, mod);
        base = mul_mod(base, base, mod);
        exp >>= 1;
    }
    return res;
}

// Імовірнісний тест простоти Міллера — Рабіна (детермінована версія для 64-бітних чисел)
static bool is_prime_miller_rabin(std::uint64_t n, int k_iterations = 7) {
    if (n < 2) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;

    std::uint64_t d = n - 1;
    int s = 0;
    while (d % 2 == 0) {
        d /= 2;
        s++;
    }

    // Детерміновані бази для n < 2^64
    static const std::uint64_t bases[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    int num_bases = sizeof(bases) / sizeof(bases[0]);
    if (k_iterations < num_bases) num_bases = k_iterations;

    for (int i = 0; i < num_bases; ++i) {
        std::uint64_t a = bases[i];
        if (n <= a) break;

        std::uint64_t x = power_mod(a, d, n);
        if (x == 1 || x == n - 1) continue;

        bool composite = true;
        for (int r = 1; r < s; ++r) {
            x = mul_mod(x, x, n);
            if (x == n - 1) {
                composite = false;
                break;
            }
        }
        if (composite) return false;
    }
    return true;
}

// Обчислення довжини ланцюжка 1-го роду, що починається з p1
static int get_chain_length(std::uint64_t p1) {
    int length = 0;
    std::uint64_t current = p1;

    while (is_prime_miller_rabin(current)) {
        length++;
        // Перевірка на можливе переповнення перед обчисленням 2 * current + 1
        if (current > (UINT64_MAX - 1) / 2) break;
        current = 2 * current + 1;
    }
    return length;
}

// Паралельний пошук ланцюжків у заданому інтервалі
void search_cunningham_chains(std::uint64_t start_val, std::uint64_t end_val, int target_k) {
    std::cout << "[C++] Пошук ланцюжків 1-го роду довжини k >= " << target_k 
              << " у діапазоні [" << start_val << ", " << end_val << "]...\n";

    std::uint64_t step = 2310;
    std::uint64_t first_m = (start_val + step) / step;

    #pragma omp parallel for schedule(dynamic, 1000)
    for (std::int64_t m = static_cast<std::int64_t>(first_m); 
         m <= static_cast<std::int64_t>(end_val / step); ++m) {
        
        std::uint64_t p1 = static_cast<std::uint64_t>(m) * step - 1;
        if (p1 < start_val || p1 > end_val) continue;

        int len = get_chain_length(p1);
        if (len >= target_k) {
            #pragma omp critical
            {
                std::cout << "Знайдено ланцюжок довжини k = " << len << "! Стартове p1 = " << p1 << "\n";
                std::uint64_t curr = p1;
                for (int i = 1; i <= len; ++i) {
                    std::cout << "  p_" << i << " = " << curr << "\n";
                    curr = 2 * curr + 1;
                }
            }
        }
    }
}

int main() {
    std::uint64_t start = 1000000ULL;
    std::uint64_t end   = 50000000ULL;
    int target_length = 5;

    double t0 = omp_get_wtime();
    search_cunningham_chains(start, end, target_length);
    double t1 = omp_get_wtime();

    std::cout << "Обчислення завершено за " << (t1 - t0) << " секунд.\n";
    return 0;
}
