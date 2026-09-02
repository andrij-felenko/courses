/* Первинна валідація щойно розпаяного чипа: WHO_AM_I плюс тест Scratchpad.
 *
 * Це контракт модуля: чого ми вимагаємо від драйвера шини, чим описуємо
 * цільовий кристал і які саме числа має нести діагностичний звіт. Жодної
 * конфігурації сенсора тут немає — на цьому етапі ми ще не знаємо, чи живий
 * кремній на тому кінці доріжок. */
#ifndef BRINGUP_H
#define BRINGUP_H

#include <stdbool.h>
#include <stdint.h>

/* Підсумок перевірки. Порядок значень — це порядок судження: спершу ловимо
 * мертву шину, і лише потім беремося тлумачити вміст байта. */
typedef enum {
    BRINGUP_OK = 0,
    BRINGUP_NO_ANSWER,        /* NACK на I2C або тайм-аут драйвера: відповіді немає взагалі */
    BRINGUP_BUS_STUCK_HIGH,   /* прочитано 0xFF: працює тільки резистор підтяжки */
    BRINGUP_BUS_STUCK_LOW,    /* прочитано 0x00: лінію притиснуто до землі */
    BRINGUP_BIT_SHIFT,        /* ID зсунуто рівно на розряд: CPOL/CPHA, частота або 8-бітна адреса */
    BRINGUP_FOREIGN_ID,       /* відповів чужий кремній або інша ревізія */
    BRINGUP_WRITE_PATH_DEAD,  /* читання живе, а запис до кристала не доходить */
    BRINGUP_SCRATCHPAD_BAD    /* запис доходить, але дані спотворені */
} bringup_status_t;

typedef enum {
    BRINGUP_SHIFT_NONE = 0,
    BRINGUP_SHIFT_LEFT,   /* прийшло (expected << 1): ведучий стробує на пів такту пізніше */
    BRINGUP_SHIFT_RIGHT   /* прийшло (expected >> 1): ведучий стробує на пів такту раніше */
} bringup_shift_t;

/* Драйвер шини. Валідації потрібно рівно три дії; ctx дає змогу тримати
 * кілька шин одночасно, не заводячи глобальних змінних.
 * read_reg/write_reg повертають false, якщо кадр не відбувся на фізичному
 * рівні (NACK, тайм-аут, втрачений арбітраж) — це НЕ те саме, що прочитаний
 * байт 0x00 чи 0xFF. */
typedef struct {
    bool (*read_reg)(void *ctx, uint8_t reg, uint8_t *out);
    bool (*write_reg)(void *ctx, uint8_t reg, uint8_t value);
    void (*delay_ms)(void *ctx, uint32_t ms);
    void *ctx;
} bus_driver_t;

/* Опис цільового чипа. t_por_ms береться з даташита (розділ Power-On Reset
 * Time), scratchpad_reg — безпечна 8-бітна комірка читання-запису. */
typedef struct {
    const char *name;
    uint8_t     id_reg;
    uint8_t     expected_id;
    uint8_t     scratchpad_reg;
    uint32_t    t_por_ms;
    uint8_t     retries;
    uint32_t    retry_delay_ms;
} chip_config_t;

/* Усе, що дізналися про вузол зв'язку за одну процедуру. */
typedef struct {
    bringup_status_t status;
    uint8_t          received_id;
    uint8_t          attempts;    /* скільки спроб читання WHO_AM_I знадобилося */
    bringup_shift_t  shift;
    bool             scratchpad_done;
    uint8_t          written;     /* патерн, на якому впав тест запису */
    uint8_t          readback;    /* що повернулося замість нього */
    uint8_t          stuck_high;  /* біти, які читаються одиницею попри записаний нуль */
    uint8_t          stuck_low;   /* біти, які читаються нулем попри записану одиницю */
    uint8_t          bridged;     /* сусідні розряди, злиті містком припою */
} diagnostic_report_t;

/* Повна послідовність: пауза t_POR, WHO_AM_I з повторними спробами,
 * класифікація аномалій, перевірка зсуву, тест Scratchpad із відновленням. */
diagnostic_report_t bringup_validate(const bus_driver_t *bus, const chip_config_t *cfg);

/* Розшифрування звіту (diagnose.c) */
const char *bringup_status_text(bringup_status_t status);
const char *bringup_first_step(const diagnostic_report_t *report);
const char *bringup_known_chip(uint8_t id_reg, uint8_t id);
void        bringup_print_report(const diagnostic_report_t *report, const chip_config_t *cfg);

#endif /* BRINGUP_H */
