#include "power.h"

#include "hal.h"

// Дільник 100k/100k на вхід АЦП, опора 3.3 В, дванадцять розрядів:
// mv = raw · 3300 · 2 / 4095. Множник поміщається в 32 біти без переповнення.
#define VBAT_NUM 6600u
#define VBAT_DEN 4095u

// Пороги для банки 18650 з гістерезисом 50 мВ: назад у спокійніший стан
// прошивка переходить лише на 50 мВ вище за поріг спрацювання.
#define LOW_TRIP_MV  3500u
#define LOW_CLEAR_MV 3550u
#define CRIT_TRIP_MV  3300u
#define CRIT_CLEAR_MV 3350u

#define RAIL_TIMEOUT_MS 50u

static uint32_t s_filt_q8;   // напруга у форматі мілівольти·256
static batt_level_t s_level = BATT_OK;

bool power_hold_on(void)
{
    // Кнопка живлення лише відкриває затвор P-канального ключа; далі його
    // тримає прошивка. Наростання dV/dt задає RC у колі затвора, тож тут
    // ми просто чекаємо, поки шина справді підніметься.
    hal_gpio_write(PIN_POWER_LATCH, true);

    uint32_t t0 = hal_millis();
    while (!hal_gpio_read(PIN_RAIL_GOOD)) {
        if (hal_millis() - t0 > RAIL_TIMEOUT_MS) {
            hal_gpio_write(PIN_POWER_LATCH, false);
            return false;   // шина не піднялася: коротке замикання або сіла банка
        }
    }
    return true;
}

void power_release(void)
{
    hal_gpio_write(PIN_POWER_LATCH, false);
}

void power_sample_battery(void)
{
    uint16_t raw = hal_adc_vbat_raw();
    uint32_t mv = ((uint32_t)raw * VBAT_NUM) / VBAT_DEN;

    if (s_filt_q8 == 0) {
        s_filt_q8 = mv << 8;   // перший відлік задає початок, а не сходинку
    } else {
        // Вага 1/256 при виклику раз на 8 мс дає сталу часу близько двох секунд.
        s_filt_q8 += ((mv << 8) - s_filt_q8) >> 8;
    }

    uint32_t v = s_filt_q8 >> 8;
    switch (s_level) {
    case BATT_OK:
        if (v < LOW_TRIP_MV) {
            s_level = BATT_LOW;
        }
        break;
    case BATT_LOW:
        if (v < CRIT_TRIP_MV) {
            s_level = BATT_CRITICAL;
        } else if (v > LOW_CLEAR_MV) {
            s_level = BATT_OK;
        }
        break;
    case BATT_CRITICAL:
        if (v > CRIT_CLEAR_MV) {
            s_level = BATT_LOW;
        }
        break;
    }
}

uint16_t power_battery_mv(void)
{
    return (uint16_t)(s_filt_q8 >> 8);
}

batt_level_t power_level(void)
{
    return s_level;
}
