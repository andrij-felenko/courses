#ifndef IEC60730_BIST_H
#define IEC60730_BIST_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди результатів самодіагностики */
typedef enum {
    BIST_OK               = 0x00,
    BIST_ERR_CPU_REG      = 0x01,
    BIST_ERR_CPU_FLAGS    = 0x02,
    BIST_ERR_CPU_PC       = 0x03,
    BIST_ERR_RAM_MARCH_C  = 0x10,
    BIST_ERR_FLASH_CRC    = 0x20,
    BIST_ERR_CLOCK_DRIFT  = 0x30,
    BIST_ERR_WDT_TRIGGER  = 0x40,
    BIST_ERR_ADC_VREF     = 0x50,
    BIST_ERR_GPIO_STUCK   = 0x60
} bist_status_t;

/* Контекст неруйнівного фонового тестування ОЗП */
typedef struct {
    uint32_t *start_addr;       /* Початкова адреса області ОЗП */
    uint32_t *end_addr;         /* Кінцева адреса області ОЗП */
    uint32_t *current_ptr;      /* Поточний вказівник на активний зріз */
    size_t    slice_words;      /* Кількість 32-бітних слів у зрізі */
    uint32_t  backup_buf[16];   /* Буфер для збереження вмісту активного зрізу (до 64 байт) */
} bist_ram_slice_ctx_t;

/* Контекст циклічної перевірки Flash */
typedef struct {
    const uint8_t *flash_start; /* Початок образу програми */
    size_t         total_bytes; /* Загальний розмір коду */
    size_t         bytes_per_slice; /* Кількість байтів на один цикл BIST */
    size_t         processed_bytes; /* Оброблено на даний момент */
    uint32_t       running_crc; /* Поточне проміжне значення CRC32 */
    uint32_t       expected_crc;/* Еталонний хеш із кінця Flash / образу */
} bist_flash_crc_ctx_t;

/* Контекст перехресного контролю тактування */
typedef struct {
    uint32_t expected_counts;   /* Очікувана кількість тактів PLL за 1 період LSI */
    uint32_t tolerance_counts;  /* Допустиме відхилення (наприклад, ±5%) */
} bist_clock_ctx_t;

/* ── Функції POST (виконуються одноразово при старті) ── */
bist_status_t bist_post_cpu_registers(void);
bist_status_t bist_post_cpu_flags(void);
bist_status_t bist_post_full_ram_march_c(uint32_t *start, uint32_t *end);
bist_status_t bist_post_flash_crc32(const uint8_t *start, size_t len, uint32_t expected);
bist_status_t bist_post_clock_check(const bist_clock_ctx_t *ctx);

/* ── Функції періодичного BIST (виконуються у робочому циклі) ── */
bist_status_t bist_slice_ram_march_c(bist_ram_slice_ctx_t *ctx);
bist_status_t bist_slice_flash_crc32(bist_flash_crc_ctx_t *ctx, bool *out_cycle_complete);

/* ── Аварійний перехід у безпечний стан ── */
void bist_enter_safe_state(bist_status_t error_code);

#ifdef __cplusplus
}
#endif

#endif /* IEC60730_BIST_H */
