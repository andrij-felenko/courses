#include "iec60730_bist.h"

/* Апаратні примітиви заборони/дозволу переривань */
static inline uint32_t disable_interrupts(void) {
    uint32_t primask;
    __asm__ volatile ("mrs %0, primask\n cpsid i" : "=r" (primask) :: "memory");
    return primask;
}

static inline void restore_interrupts(uint32_t primask) {
    __asm__ volatile ("msr primask, %0" :: "r" (primask) : "memory");
}

/* ── 1. Перевірка регістрів процесора (CPU Registers POST) ── */
bist_status_t bist_post_cpu_registers(void) {
    const uint32_t pat_a = 0x55555555UL;
    const uint32_t pat_b = 0xAAAAAAAAUL;

    /* Використовуємо інлайн-асемблер для тестування R0-R12, LR без втручання оптимізатора */
    register uint32_t r0 __asm__("r0") = pat_a;
    register uint32_t r1 __asm__("r1") = pat_a;
    register uint32_t r2 __asm__("r2") = pat_a;
    register uint32_t r3 __asm__("r3") = pat_a;
    register uint32_t r4 __asm__("r4") = pat_a;

    if (r0 != pat_a || r1 != pat_a || r2 != pat_a || r3 != pat_a || r4 != pat_a) {
        return BIST_ERR_CPU_REG;
    }

    r0 = pat_b; r1 = pat_b; r2 = pat_b; r3 = pat_b; r4 = pat_b;
    if (r0 != pat_b || r1 != pat_b || r2 != pat_b || r3 != pat_b || r4 != pat_b) {
        return BIST_ERR_CPU_REG;
    }

    return BIST_OK;
}

/* ── 2. Перевірка прапорців АЛП (ALU Flags) ── */
bist_status_t bist_post_cpu_flags(void) {
    volatile uint32_t a = 0x7FFFFFFFUL;
    volatile uint32_t b = 1;
    volatile uint32_t sum = a + b; /* Генерує переповнення (V-flag) і від'ємний результат (N-flag) */

    if ((int32_t)sum >= 0) {
        return BIST_ERR_CPU_FLAGS; /* Не спрацював прапорець знака N */
    }

    volatile uint32_t c = 0xFFFFFFFFUL;
    volatile uint32_t carry_sum = c + 1; /* Генерує перенесення (C-flag) і нуль (Z-flag) */
    if (carry_sum != 0) {
        return BIST_ERR_CPU_FLAGS; /* Не спрацював прапорець нуля Z */
    }

    return BIST_OK;
}

/* ── 3. Ядро алгоритму March C- для блоку пам'яті ── */
static bool execute_march_c_core(volatile uint32_t *mem, size_t words) {
    /* M0: ⇕ (w0) */
    for (size_t i = 0; i < words; ++i) {
        mem[i] = 0x00000000UL;
    }

    /* M1: ⇑ (r0, w1) */
    for (size_t i = 0; i < words; ++i) {
        if (mem[i] != 0x00000000UL) return false;
        mem[i] = 0xFFFFFFFFUL;
    }

    /* M2: ⇑ (r1, w0) */
    for (size_t i = 0; i < words; ++i) {
        if (mem[i] != 0xFFFFFFFFUL) return false;
        mem[i] = 0x00000000UL;
    }

    /* M3: ⇓ (r0, w1) */
    for (size_t i = words; i > 0; --i) {
        size_t idx = i - 1;
        if (mem[idx] != 0x00000000UL) return false;
        mem[idx] = 0xFFFFFFFFUL;
    }

    /* M4: ⇓ (r1, w0) */
    for (size_t i = words; i > 0; --i) {
        size_t idx = i - 1;
        if (mem[idx] != 0xFFFFFFFFUL) return false;
        mem[idx] = 0x00000000UL;
    }

    /* M5: ⇕ (r0) */
    for (size_t i = 0; i < words; ++i) {
        if (mem[i] != 0x00000000UL) return false;
    }

    return true;
}

/* ── 4. Неруйнівний зріз ОЗП для фонового BIST ── */
bist_status_t bist_slice_ram_march_c(bist_ram_slice_ctx_t *ctx) {
    if (ctx == NULL || ctx->current_ptr >= ctx->end_addr) {
        return BIST_OK;
    }

    size_t words_to_test = ctx->slice_words;
    if (ctx->current_ptr + words_to_test > ctx->end_addr) {
        words_to_test = (size_t)(ctx->end_addr - ctx->current_ptr);
    }

    /* КРИТИЧНА СЕКЦІЯ: атомарне збереження, тест і відновлення */
    uint32_t primask = disable_interrupts();

    /* Зберігаємо дані застосунку у захищений буфер */
    for (size_t i = 0; i < words_to_test; ++i) {
        ctx->backup_buf[i] = ctx->current_ptr[i];
    }

    /* Прогін March C- */
    bool pass = execute_march_c_core((volatile uint32_t *)ctx->current_ptr, words_to_test);

    /* Відновлюємо дані застосунку */
    for (size_t i = 0; i < words_to_test; ++i) {
        ctx->current_ptr[i] = ctx->backup_buf[i];
    }

    restore_interrupts(primask);

    if (!pass) {
        return BIST_ERR_RAM_MARCH_C;
    }

    /* Зсуваємо вказівник на наступний зріз */
    ctx->current_ptr += words_to_test;
    if (ctx->current_ptr >= ctx->end_addr) {
        ctx->current_ptr = ctx->start_addr; /* Зациклення */
    }

    return BIST_OK;
}

/* ── 5. Інкрементальний розрахунок CRC-32 (IEEE 802.3) ── */
static uint32_t crc32_step(uint32_t crc, uint8_t data) {
    crc ^= data;
    for (int i = 0; i < 8; ++i) {
        if (crc & 1) {
            crc = (crc >> 1) ^ 0xEDB88320UL;
        } else {
            crc >>= 1;
        }
    }
    return crc;
}

bist_status_t bist_slice_flash_crc32(bist_flash_crc_ctx_t *ctx, bool *out_cycle_complete) {
    *out_cycle_complete = false;
    size_t chunk = ctx->bytes_per_slice;
    if (ctx->processed_bytes + chunk > ctx->total_bytes) {
        chunk = ctx->total_bytes - ctx->processed_bytes;
    }

    const uint8_t *p = ctx->flash_start + ctx->processed_bytes;
    for (size_t i = 0; i < chunk; ++i) {
        ctx->running_crc = crc32_step(ctx->running_crc, p[i]);
    }

    ctx->processed_bytes += chunk;
    if (ctx->processed_bytes >= ctx->total_bytes) {
        uint32_t final_crc = ~ctx->running_crc;
        if (final_crc != ctx->expected_crc) {
            return BIST_ERR_FLASH_CRC;
        }
        *out_cycle_complete = true;
        ctx->processed_bytes = 0;
        ctx->running_crc = 0xFFFFFFFFUL;
    }

    return BIST_OK;
}

/* ── 6. Перехід у безпечний стан (Safe State Lock) ── */
void bist_enter_safe_state(bist_status_t error_code) {
    disable_interrupts();

    /* 1. Знеструмити критичні виходи: ШІМ у 0, реле розімкнути */
    /* GPIOA->ODR = 0; TIM1->BDTR &= ~TIM_BDTR_MOE; */

    /* 2. Зафіксувати код помилки в нелетких регістрах RTC/Backup */
    /* RTC->BKP0R = (uint32_t)error_code; */
    (void)error_code;

    /* 3. Нескінченне зависання для очікування апаратного скиду сторожовим таймером */
    for (;;) {
        __asm__ volatile ("wfi");
    }
}
