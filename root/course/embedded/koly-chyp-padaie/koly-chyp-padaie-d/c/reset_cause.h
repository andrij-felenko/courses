#ifndef RESET_CAUSE_H
#define RESET_CAUSE_H

#include <stdbool.h>
#include <stdint.h>

/* Джерела скидання; результат зчитування — маска цих бітів. */
enum {
    RESET_SRC_POWER_ON  = 1u << 0,
    RESET_SRC_BROWNOUT  = 1u << 1,
    RESET_SRC_PIN       = 1u << 2,
    RESET_SRC_IWDG      = 1u << 3,
    RESET_SRC_WWDG      = 1u << 4,
    RESET_SRC_SOFTWARE  = 1u << 5,
    RESET_SRC_LOW_POWER = 1u << 6
};

/*
 * Зчитує RCC->CSR і НЕГАЙНО стирає липкі прапорці бітом RMVF.
 * Викликати першою дією в main(): після стирання апаратура вже нічого не
 * пам'ятає, тому повторні виклики віддають збережену копію першого зчитування.
 */
uint32_t reset_cause_capture(void);

/* Маска з першого виклику capture (0, якщо capture ще не було). */
uint32_t reset_cause_last(void);

/* Сире значення RCC->CSR на мить зчитування — на випадок нестандартних бітів. */
uint32_t reset_cause_raw_csr(void);

void reset_cause_print(uint32_t mask);

/* true, якщо перезапуск виглядає як наслідок програмного краху, а не подача живлення. */
bool reset_cause_is_crash(uint32_t mask);

#endif /* RESET_CAUSE_H */
