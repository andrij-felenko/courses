/* Безпечне модульне піднесення до степеня в константному часі */
uint64_t mont_pow_ladder64(const mont_ctx64_t *ctx, uint64_t base, uint64_t exp) {
    /* 1. Переведення основи у простір Монтгомері */
    uint64_t x_bar = mont_to_domain64(ctx, base);
    
    /* 2. Ініціалізація регістрів драбини у просторі Монтгомері:
          r0 = 1 (в образі Монтгомері це R mod N)
          r1 = base (в образі Монтгомері це x_bar) */
    uint64_t r0 = ctx->r_mod_n;
    uint64_t r1 = x_bar;
    
    /* 3. Прохід по всіх 64 бітах від старшого до молодшого */
    for (int i = 63; i >= 0; --i) {
        uint64_t bit = (exp >> i) & 1;
        
        /* Застосовуємо константний умовний обмін регістрів (cswap) */
        uint64_t mask = -bit;
        uint64_t diff = (r0 ^ r1) & mask;
        r0 ^= diff;
        r1 ^= diff;
        
        /* Обчислення: R1 = R0 * R1, R0 = R0^2 */
        r1 = mont_mul64(ctx, r0, r1);
        r0 = mont_mul64(ctx, r0, r0);
        
        /* Зворотний обмін для повернення регістрів на свої місця */
        diff = (r0 ^ r1) & mask;
        r0 ^= diff;
        r1 ^= diff;
    }
    
    /* 4. Повернення результату з простору Монтгомері */
    return mont_from_domain64(ctx, r0);
}
