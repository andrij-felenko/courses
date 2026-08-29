#ifndef FCT_H
#define FCT_H

#include <stdbool.h>
#include <stdint.h>

#include "hal.h"

/* Ядро тестового рушія: код результату, вердикт і дескриптор тесту.
 * Жодного динамічного виділення: усі рядки — літерали в прошивці,
 * усі числа лежать у самому вердикті. */

typedef enum {
    FCT_PASS = 0,
    FCT_FAIL = 1,
    FCT_TIMEOUT = 2,
    FCT_BUS_LOCKED = 3,
    FCT_INVALID_ID = 4,
    FCT_SKIPPED = 5
} fct_result_t;

typedef struct {
    fct_result_t code;
    const char  *detail;   /* завжди рядковий літерал — копіювати нічого */
    int32_t      value;    /* число, осмислене для цього тесту */
    const char  *unit;     /* "mV", "uA", "ppm", "ddBm", NULL — без числа */
} fct_verdict_t;

typedef void (*fct_test_fn)(fct_verdict_t *v);

typedef struct {
    const char *name;
    fct_test_fn run;
    uint32_t    budget_us;  /* детермінований бюджет часу на тест */
    bool        blocking;   /* провал зупиняє весь набір */
} fct_case_t;

/* --- Дедлайн: єдиний спосіб чекати на апаратуру ------------------------- */

typedef struct {
    uint32_t start_us;
    uint32_t limit_us;
} fct_deadline_t;

static inline fct_deadline_t fct_deadline_start(uint32_t limit_us)
{
    fct_deadline_t d;
    d.start_us = hal_time_us();
    d.limit_us = limit_us;
    return d;
}

static inline uint32_t fct_elapsed_us(const fct_deadline_t *d)
{
    return hal_time_us() - d->start_us;  /* беззнакова різниця переживає обгортку */
}

static inline bool fct_expired(const fct_deadline_t *d)
{
    return fct_elapsed_us(d) >= d->limit_us;
}

/* --- Заповнення вердикту ------------------------------------------------ */

static inline void fct_pass(fct_verdict_t *v, const char *note,
                            int32_t value, const char *unit)
{
    v->code = FCT_PASS;
    v->detail = note;
    v->value = value;
    v->unit = unit;
}

static inline void fct_fail(fct_verdict_t *v, fct_result_t code,
                            const char *detail)
{
    v->code = code;
    v->detail = detail;
    v->value = 0;
    v->unit = NULL;
}

static inline void fct_fail_at(fct_verdict_t *v, fct_result_t code,
                               const char *detail, int32_t value,
                               const char *unit)
{
    v->code = code;
    v->detail = detail;
    v->value = value;
    v->unit = unit;
}

/* --- Набір тестів ------------------------------------------------------- */

void test_power_rails(fct_verdict_t *v);
void test_clock_pll(fct_verdict_t *v);
void test_ram_march(fct_verdict_t *v);
void test_i2c_devices(fct_verdict_t *v);
void test_spi_flash(fct_verdict_t *v);
void test_rf_cw(fct_verdict_t *v);
void test_otp_trim(fct_verdict_t *v);

/* Напруга аналогового домену через VREFINT — потрібна і тесту живлення,
 * і сторожуванню запису OTP. */
bool fct_read_vdda_mv(int32_t *mv);

#endif /* FCT_H */
