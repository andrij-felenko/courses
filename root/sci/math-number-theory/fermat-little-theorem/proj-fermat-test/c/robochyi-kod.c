#include <stdint.h>
#include <stdbool.h>

// a·b mod m без переповнення: добуток двох майже-64-бітних чисел не влазить
// у 64 біти, тож множимо у 128-бітному проміжку й лише тоді беремо остачу.
static uint64_t mulmod(uint64_t a, uint64_t b, uint64_t m) {
    return (uint64_t)((unsigned __int128)a * b % m);
}

static uint64_t powmod(uint64_t base, uint64_t exp, uint64_t m) {
    uint64_t result = 1;
    base %= m;
    while (exp > 0) {
        if (exp & 1) result = mulmod(result, base, m);  // домножити сходинку
        base = mulmod(base, base, m);                   // наступний квадрат
        exp >>= 1;
    }
    return result;
}

bool is_probable_prime(uint64_t n, const uint64_t *bases, int k) {
    if (n < 4)      return n == 2 || n == 3;
    if (n % 2 == 0) return false;
    for (int i = 0; i < k; i++) {
        uint64_t a = bases[i] % n;
        if (a < 2) continue;                 // основи 0 та 1 нічого не кажуть
        if (powmod(a, n - 1, n) != 1)        // свідок складеності
            return false;                    // n напевно складене
    }
    return true;                             // імовірно просте
}
