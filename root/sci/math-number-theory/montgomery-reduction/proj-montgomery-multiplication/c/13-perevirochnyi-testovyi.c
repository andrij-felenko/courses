int main(void) {
    uint64_t n = 1000000007ULL; /* Просте непарне число */
    mont_ctx64_t ctx;
    
    if (!mont_ctx64_init(&ctx, n)) {
        printf("Помилка ініціалізації контексту!\n");
        return 1;
    }
    
    uint64_t a = 123456789ULL;
    uint64_t b = 987654321ULL;
    uint64_t expected_mul = (unsigned __int128)a * b % n;
    
    uint64_t a_bar = mont_to_domain64(&ctx, a);
    uint64_t b_bar = mont_to_domain64(&ctx, b);
    uint64_t c_bar = mont_mul64(&ctx, a_bar, b_bar);
    uint64_t actual_mul = mont_from_domain64(&ctx, c_bar);
    
    printf("Множення: очікувано = %llu, отримано = %llu [%s]\n",
           expected_mul, actual_mul, (expected_mul == actual_mul) ? "OK" : "FAIL");
    
    /* Тест піднесення до степеня: a^exp mod n */
    uint64_t exp = 65537ULL;
    uint64_t res_pow = mont_pow_ladder64(&ctx, a, exp);
    printf("Піднесення до степеня %llu^%llu mod %llu = %llu\n", a, exp, n, res_pow);
    
    /* Тест пакетного обернення 3 чисел */
    uint64_t vals[3] = {123, 456, 789};
    uint64_t invs[3];
    mont_batch_invert64(&ctx, vals, invs, 3);
    for (int i = 0; i < 3; ++i) {
        uint64_t check = (unsigned __int128)vals[i] * invs[i] % n;
        printf("Обернення %llu^-1 mod %llu = %llu (перевірка = %llu)\n",
               vals[i], n, invs[i], check);
    }
    
    return 0;
}
