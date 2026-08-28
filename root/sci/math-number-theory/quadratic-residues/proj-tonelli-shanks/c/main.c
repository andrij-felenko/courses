/* C11 / Posix implementation of Tonelli-Shanks Algorithm */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Безпечне 64-бітне множення за модулем: (a * b) % mod з захистом від переповнення */
static uint64_t mul_mod(uint64_t a, uint64_t b, uint64_t mod) {
#if defined(__SIZEOF_INT128__)
    return (uint64_t)(((unsigned __int128)a * b) % mod);
#else
    uint64_t res = 0;
    a %= mod;
    while (b > 0) {
        if (b & 1) res = (res + a >= mod) ? (res + a - mod) : (res + a);
        a = (a + a >= mod) ? (a + a - mod) : (a + a);
        b >>= 1;
    }
    return res;
#endif
}

/* Модульне піднесення до степеня: (base^exp) % mod */
static uint64_t pow_mod(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) res = mul_mod(res, base, mod);
        base = mul_mod(base, base, mod);
        exp >>= 1;
    }
    return res;
}

/* Обчислення символу Лежандра (a / p) через критерій Ейлера */
int legendre_symbol(uint64_t a, uint64_t p) {
    if (a % p == 0) return 0;
    uint64_t res = pow_mod(a, (p - 1) / 2, p);
    return (res == 1) ? 1 : -1;
}

/* Обчислення символу Якобі (a / n) для довільного непарного n */
int jacobi_symbol(int64_t a, int64_t n) {
    if (n <= 0 || (n & 1) == 0) return 0;
    a %= n;
    if (a < 0) a += n;
    
    int result = 1;
    while (a != 0) {
        while ((a & 1) == 0) {
            a >>= 1;
            int64_t n_mod8 = n & 7;
            if (n_mod8 == 3 || n_mod8 == 5) {
                result = -result;
            }
        }
        int64_t temp = a;
        a = n;
        n = temp;
        
        if ((a & 3) == 3 && (n & 3) == 3) {
            result = -result;
        }
        a %= n;
    }
    return (n == 1) ? result : 0;
}

/* Розв'язання рівняння x^2 ≡ a (mod p) алгоритмом Тонеллі-Шенкса */
bool tonelli_shanks(uint64_t a, uint64_t p, uint64_t *root1, uint64_t *root2) {
    a %= p;
    if (a == 0) {
        *root1 = 0;
        *root2 = 0;
        return true;
    }
    
    if (legendre_symbol(a, p) != 1) {
        return false; /* Квадратичний нелишок — розв'язків немає */
    }
    
    /* Окремий випадок p ≡ 3 (mod 4) */
    if ((p & 3) == 3) {
        uint64_t r = pow_mod(a, (p + 1) / 4, p);
        *root1 = r;
        *root2 = p - r;
        return true;
    }
    
    /* 1. Факторизація p - 1 = q * 2^s */
    uint64_t q = p - 1;
    uint64_t s = 0;
    while ((q & 1) == 0) {
        q >>= 1;
        s++;
    }
    
    /* 2. Пошук нелишку z */
    uint64_t z = 2;
    while (legendre_symbol(z, p) != -1) {
        z++;
    }
    
    /* 3. Ініціалізація інваріантів */
    uint64_t c = pow_mod(z, q, p);
    uint64_t r = pow_mod(a, (q + 1) / 2, p);
    uint64_t t = pow_mod(a, q, p);
    uint64_t m = s;
    
    /* 4. Основний цикл зменшення порядків */
    while (t != 1) {
        uint64_t t2i = t;
        uint64_t i = 0;
        for (i = 1; i < m; i++) {
            t2i = mul_mod(t2i, t2i, p);
            if (t2i == 1) break;
        }
        
        if (i == m) return false; /* Захист (не повинен спрацювати) */
        
        uint64_t b = pow_mod(c, 1ULL << (m - i - 1), p);
        r = mul_mod(r, b, p);
        uint64_t b2 = mul_mod(b, b, p);
        t = mul_mod(t, b2, p);
        c = b2;
        m = i;
    }
    
    *root1 = r;
    *root2 = p - r;
    return true;
}

int main(void) {
    uint64_t p = 1000000007ULL; /* 10^9 + 7 */
    uint64_t a = 5ULL;
    uint64_t r1 = 0, r2 = 0;
    
    if (tonelli_shanks(a, p, &r1, &r2)) {
        printf("Квадратні корені з %glu mod %glu: %glu та %glu\n", 
               (double)a, (double)p, (double)r1, (double)r2);
        printf("Перевірка: (%glu^2) mod %glu = %glu\n", 
               (double)r1, (double)p, (double)mul_mod(r1, r1, p));
    } else {
        printf("Число %glu не є квадратичним лишком mod %glu\n", (double)a, (double)p);
    }
    return 0;
}
