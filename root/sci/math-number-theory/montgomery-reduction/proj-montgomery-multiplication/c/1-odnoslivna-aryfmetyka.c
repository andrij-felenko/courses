#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

/* Структура контексту Монтгомері для 64-бітового модуля */
typedef struct {
    uint64_t n;      /* Непарний модуль N */
    uint64_t n_prime;/* Константа N' = -N^-1 mod 2^64 */
    uint64_t r_mod_n;/* Константа R mod N = (2^64) mod N */
    uint64_t r2_mod_n;/* Константа R^2 mod N = (2^128) mod N */
} mont_ctx64_t;

/* Обчислення константи n_prime = -n^-1 mod 2^64 за допомогою піднесення Гензеля */
uint64_t mont_compute_nprime64(uint64_t n) {
    uint64_t x = 1; /* Початкове наближення (1 біт для непарного N) */
    /* 6 ітерацій Ньютона подвоюють точність: 1 -> 2 -> 4 -> 8 -> 16 -> 32 -> 64 біти */
    x = x * (2 - n * x);
    x = x * (2 - n * x);
    x = x * (2 - n * x);
    x = x * (2 - n * x);
    x = x * (2 - n * x);
    x = x * (2 - n * x);
    return -x; /* Унарний мінус дає -N^-1 mod 2^64 */
}

/* Ініціалізація контексту Монтгомері */
bool mont_ctx64_init(mont_ctx64_t *ctx, uint64_t n) {
    if ((n & 1) == 0 || n <= 1) {
        return false; /* Модуль має бути непарним і більшим за 1 */
    }
    ctx->n = n;
    ctx->n_prime = mont_compute_nprime64(n);
    
    /* Обчислення R mod N = (2^64) mod N */
    unsigned __int128 r = ((unsigned __int128)1) << 64;
    ctx->r_mod_n = (uint64_t)(r % n);
    
    /* Обчислення R^2 mod N = (2^128) mod N для швидкого переведення чисел у простір Монтгомері */
    unsigned __int128 r2 = (r % n) * (r % n);
    ctx->r2_mod_n = (uint64_t)(r2 % n);
    
    return true;
}

/* Базовий алгоритм редукції Монтгомері: обчислює (T * R^-1) mod N */
uint64_t mont_redc64(const mont_ctx64_t *ctx, unsigned __int128 T) {
    uint64_t t_low = (uint64_t)T;
    uint64_t m = t_low * ctx->n_prime; /* m = (T mod R) * N' mod R */
    
    unsigned __int128 mn = (unsigned __int128)m * ctx->n;
    unsigned __int128 sum = T + mn;
    
    uint64_t t = (uint64_t)(sum >> 64); /* Точне ділення на R = 2^64 через зсув */
    
    /* Фінальне зведення: якщо t >= N, віднімаємо N */
    if (t >= ctx->n) {
        t -= ctx->n;
    }
    return t;
}

/* Переведення класичного числа у простір Монтгомері: ā = a * R mod N */
uint64_t mont_to_domain64(const mont_ctx64_t *ctx, uint64_t a) {
    return mont_redc64(ctx, (unsigned __int128)a * ctx->r2_mod_n);
}

/* Повернення числа з простору Монтгомері: a = REDC(ā) */
uint64_t mont_from_domain64(const mont_ctx64_t *ctx, uint64_t a_bar) {
    return mont_redc64(ctx, (unsigned __int128)a_bar);
}

/* Множення двох чисел у просторі Монтгомері: c̄ = ā * b̄ * R^-1 mod N */
uint64_t mont_mul64(const mont_ctx64_t *ctx, uint64_t a_bar, uint64_t b_bar) {
    return mont_redc64(ctx, (unsigned __int128)a_bar * b_bar);
}
