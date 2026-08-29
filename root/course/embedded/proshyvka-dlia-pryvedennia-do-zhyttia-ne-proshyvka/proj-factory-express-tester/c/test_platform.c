/* Фаза 0: живлення й тактування. Доки ці два тести не пройшли, енергоємні
 * модулі (радіо, пропалювання OTP) не вмикають узагалі. */

#include "fct.h"
#include "hal.h"

#define VREFINT_CAL_MV     3000   /* калібрування VREFINT зняте при 3.000 В */
#define ADC_FULL_SCALE     4095
#define VDDA_NOMINAL_MV    3300
#define VCORE_NOMINAL_MV   1800
#define VCORE_DIVIDER      2      /* V_CORE заведено на АЦП через дільник 1:2 */
#define RAIL_TOLERANCE_PCT 3

#define INRUSH_LIMIT_MA    400
#define INRUSH_LIMIT_US    3000
#define IQ_MIN_UA          100
#define IQ_MAX_UA          2500

#define HSE_NOMINAL_HZ     24000000u
#define HSE_TOLERANCE_HZ   12000u    /* ±500 ppm — груба перевірка збудження */
#define PLL_LOCK_TIMEOUT_US 5000u

bool fct_read_vdda_mv(int32_t *mv)
{
    uint16_t raw = 0;
    if (!hal_adc_read(HAL_ADC_CH_VREFINT, &raw, 2000)) {
        return false;
    }
    if (raw == 0) {
        return false;  /* канал VREFINT мовчить — АЦП не запустився */
    }
    /* V_DDA = 3.000 В * CAL / RAW: чим вища живлення, тим менший код VREFINT. */
    *mv = ((int32_t)VREFINT_CAL_MV * (int32_t)hal_vrefint_cal()) / (int32_t)raw;
    return true;
}

static bool within_tolerance(int32_t value_mv, int32_t nominal_mv)
{
    int32_t delta = value_mv - nominal_mv;
    if (delta < 0) {
        delta = -delta;
    }
    return delta * 100 <= nominal_mv * RAIL_TOLERANCE_PCT;
}

void test_power_rails(fct_verdict_t *v)
{
    /* Крок 1–2 зняв сам стенд ще до відпускання RESET: прошивка лише
     * забирає журнал і виносить по ньому вердикт. */
    hal_stand_power_t log;
    if (!hal_stand_read_power_log(&log, 50000)) {
        fct_fail(v, FCT_TIMEOUT, "Стенд не віддав журнал фази 0");
        return;
    }

    if (log.inrush_peak_ma > INRUSH_LIMIT_MA &&
        log.inrush_duration_us > INRUSH_LIMIT_US) {
        fct_fail_at(v, FCT_FAIL, "Струм ввімкнення: коротке в силовій шині",
                    log.inrush_peak_ma, "mA");
        return;
    }
    if (log.iq_ua > IQ_MAX_UA) {
        fct_fail_at(v, FCT_FAIL,
                    "Струм спокою завищений: діоди захисту, BGA або флюс",
                    log.iq_ua, "uA");
        return;
    }
    if (log.iq_ua < IQ_MIN_UA) {
        fct_fail_at(v, FCT_FAIL, "Струм спокою нижчий за норму: плата не живиться",
                    log.iq_ua, "uA");
        return;
    }

    /* Крок 3: внутрішній моніторинг рейок після відпускання RESET. */
    int32_t vdda_mv = 0;
    if (!fct_read_vdda_mv(&vdda_mv)) {
        fct_fail(v, FCT_TIMEOUT, "АЦП: канал VREFINT не відповідає");
        return;
    }
    if (!within_tolerance(vdda_mv, VDDA_NOMINAL_MV)) {
        fct_fail_at(v, FCT_FAIL, "V_DDA поза допуском ±3%", vdda_mv, "mV");
        return;
    }

    uint16_t core_raw = 0;
    if (!hal_adc_read(HAL_ADC_CH_VCORE, &core_raw, 2000)) {
        fct_fail(v, FCT_TIMEOUT, "АЦП: канал V_CORE не відповідає");
        return;
    }
    int32_t vcore_mv = ((int32_t)core_raw * vdda_mv * VCORE_DIVIDER) / ADC_FULL_SCALE;
    if (!within_tolerance(vcore_mv, VCORE_NOMINAL_MV)) {
        fct_fail_at(v, FCT_FAIL, "V_CORE поза допуском ±3%", vcore_mv, "mV");
        return;
    }

    fct_pass(v, "Рейки в допуску", vcore_mv, "mV");
}

void test_clock_pll(fct_verdict_t *v)
{
    uint32_t hse_hz = hal_clock_measure_hse_hz(10);
    if (hse_hz == 0) {
        fct_fail(v, FCT_FAIL, "HSE не збуджується: кварц або навантажувальні C");
        return;
    }
    int32_t drift = (int32_t)hse_hz - (int32_t)HSE_NOMINAL_HZ;
    if (drift < 0) {
        drift = -drift;
    }
    if ((uint32_t)drift > HSE_TOLERANCE_HZ) {
        fct_fail_at(v, FCT_FAIL, "Частота HSE поза грубим допуском",
                    (int32_t)hse_hz, "Hz");
        return;
    }

    hal_clock_pll_start();
    fct_deadline_t d = fct_deadline_start(PLL_LOCK_TIMEOUT_US);
    while (!hal_clock_pll_locked()) {
        if (fct_expired(&d)) {
            /* Саме тут звичайна прошивка вішається в while(!LOCK): у тестері
             * очікування завжди має дно. */
            fct_fail(v, FCT_TIMEOUT, "PLL не захопився за 5 мс");
            return;
        }
    }

    fct_pass(v, "HSE збуджений, PLL захопився", (int32_t)fct_elapsed_us(&d), "us");
}
