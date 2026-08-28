#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* ── 1. Багатозначні токени стану (Hamming Distance = 32) ────────── */
typedef uint32_t secure_token_t;

#define SECURE_TOKEN_TRUE      ((secure_token_t)0x55AA55AAU)
#define SECURE_TOKEN_FALSE     ((secure_token_t)0xAA55AA55U)
#define SECURE_TOKEN_INIT      ((secure_token_t)0x3C3C3C3CU)
#define SECURE_TOKEN_PANIC     ((secure_token_t)0xFFFFFFFFU)

/* Канарейки етапів виконання */
#define STEP_CANARY_INIT       ((uint32_t)0x6A09E667U)
#define STEP_CANARY_STAGE1     ((uint32_t)0xBB67AE85U)
#define STEP_CANARY_STAGE2     ((uint32_t)0x3C6EF372U)
#define STEP_CANARY_FINAL      ((uint32_t)0xA54FF53AU)

/* Бар'єр оптимізації компілятора (запобігає об'єднанню перевірок) */
#define HARDENED_BARRIER(var)  __asm__ volatile("" : "+r" (var) : : "memory")

/* ── 2. Гарантоване очищення пам'яті від секретних ключів ───────── */
void secure_zeroize(void *ptr, size_t len) {
    if (!ptr || len == 0) return;
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0U;
    }
    __asm__ volatile("" : : "r"(ptr) : "memory");
}

/* ── 3. Панічна пастка при виявленні спроби зламу ────────────────── */
__attribute__((noreturn)) void secure_panic_trap(void) {
    /* Відключення переривань для блокування обробників */
    __asm__ volatile("cpsid i" : : : "memory");

    /* Занулення внутрішніх регістрів загального призначення */
    register uint32_t r0 __asm__("r0") = 0;
    register uint32_t r1 __asm__("r1") = 0;
    register uint32_t r2 __asm__("r2") = 0;
    register uint32_t r3 __asm__("r3") = 0;
    __asm__ volatile("" : : "r"(r0), "r"(r1), "r"(r2), "r"(r3));

    /* Нескінченний цикл блокування ядра */
    while (1) {
        __asm__ volatile("wfi");
    }
}

/* ── 4. Порівняння пам'яті з постійним часом виконання ─────────── */
secure_token_t hardened_memcmp(const void *buf_a, const void *buf_b, size_t len) {
    if (!buf_a || !buf_b) return SECURE_TOKEN_FALSE;

    const volatile uint8_t *a = (const volatile uint8_t *)buf_a;
    const volatile uint8_t *b = (const volatile uint8_t *)buf_b;
    volatile uint32_t diff_acc = 0U;

    for (size_t i = 0; i < len; ++i) {
        diff_acc |= ((uint32_t)a[i] ^ (uint32_t)b[i]);
    }
    HARDENED_BARRIER(diff_acc);

    /* Обчислення без умовних переходів:
       Якщо diff_acc == 0: mask = 0x00000000;
       Якщо diff_acc != 0: mask = 0xFFFFFFFF; */
    uint32_t is_zero_mask = (uint32_t)(((int32_t)(diff_acc | (0U - diff_acc))) >> 31);

    secure_token_t result = (SECURE_TOKEN_TRUE & ~is_zero_mask) | (SECURE_TOKEN_FALSE & is_zero_mask);
    HARDENED_BARRIER(result);
    return result;
}

/* ── 5. Програмне внесення часового шуму (Software Jitter) ──────── */
void hardened_delay_jitter(uint32_t entropy) {
    /* Додаємо псевдовипадкову кількість циклів від 16 до 64 */
    volatile uint32_t loops = (entropy & 0x3FU) + 16U;
    while (loops > 0U) {
        loops--;
        HARDENED_BARRIER(loops);
    }
}

/* ── 6. Захищена двохетапна перевірка автентичності ─────────────── */
secure_token_t hardened_verify_payload(const uint8_t *computed_mac,
                                       const uint8_t *expected_mac,
                                       size_t mac_len,
                                       uint32_t entropy) {
    volatile uint32_t canary = STEP_CANARY_INIT;
    volatile secure_token_t check1 = SECURE_TOKEN_INIT;
    volatile secure_token_t check2 = SECURE_TOKEN_INIT;

    /* Етап 1: Перше пряме порівняння */
    check1 = hardened_memcmp(computed_mac, expected_mac, mac_len);
    canary ^= STEP_CANARY_STAGE1;
    HARDENED_BARRIER(check1);
    HARDENED_BARRIER(canary);

    /* Часова десинхронізація для зриву трасування збоїв */
    hardened_delay_jitter(entropy);

    /* Етап 2: Зворотне порівняння */
    check2 = hardened_memcmp(expected_mac, computed_mac, mac_len);
    canary ^= STEP_CANARY_STAGE2;
    HARDENED_BARRIER(check2);
    HARDENED_BARRIER(canary);

    /* Валідація цілісності потоку виконання */
    uint32_t expected_canary = STEP_CANARY_INIT ^ STEP_CANARY_STAGE1 ^ STEP_CANARY_STAGE2;
    if (canary != expected_canary) {
        /* Ін'єкція збою пропустила інструкції етапів */
        secure_panic_trap();
    }

    /* Підсумкова перевірка стану через побітову кореляцію */
    if ((check1 == SECURE_TOKEN_TRUE) && (check2 == SECURE_TOKEN_TRUE)) {
        /* Додатковий контроль відмови тригера в умовному переході */
        if (check1 != SECURE_TOKEN_TRUE || check2 != SECURE_TOKEN_TRUE) {
            secure_panic_trap();
        }
        return SECURE_TOKEN_TRUE;
    }

    if ((check1 == SECURE_TOKEN_FALSE) || (check2 == SECURE_TOKEN_FALSE)) {
        return SECURE_TOKEN_FALSE;
    }

    /* Якщо стан токенів виявився пошкодженим або невизначеним */
    secure_panic_trap();
}
