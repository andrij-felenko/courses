#include <stdint.h>
#include <stddef.h>

#if defined(USE_VALGRIND_CTGRIND)
#include <valgrind/memcheck.h>
#define CT_POISON(addr, len)   VALGRIND_MAKE_MEM_UNDEFINED(addr, len)
#define CT_UNPOISON(addr, len) VALGRIND_MAKE_MEM_DEFINED(addr, len)
#else
#define CT_POISON(addr, len)   ((void)0)
#define CT_UNPOISON(addr, len) ((void)0)
#endif

/* Приклад використання taint-аналізу для верифікації криптографічної обробки */
int verify_signature_instrumented(const uint8_t *secret_key, const uint8_t *sig, size_t len) {
    uint8_t expected_sig[32];
    
    /* 1. Позначаємо секретний ключ як отруєний (таємний) */
    CT_POISON(secret_key, 32);

    /* 2. Обчислюємо очікуваний підпис (усі проміжні значення автоматично отруюються) */
    for (size_t i = 0; i < 32; ++i) {
        expected_sig[i] = secret_key[i] ^ 0x36;
    }

    /* 3. Порівнюємо підписи безпечною функцією ct_memcmp */
    int is_valid = ct_memcmp(expected_sig, sig, len);

    /* 4. Результат перевірки розсекречуємо для прийняття рішення програмою */
    CT_UNPOISON(&is_valid, sizeof(is_valid));
    return is_valid;
}
