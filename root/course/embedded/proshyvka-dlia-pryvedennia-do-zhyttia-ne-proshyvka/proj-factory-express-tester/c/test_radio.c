/* Радіотракт: неперервна несуча на трьох каналах, підстроювання кварцу
 * за виміром стенда й запис знайденого коду в OTP. Жодного з'єднання
 * з мережею — на конвеєрі на це немає ні часу, ні чистого ефіру. */

#include "fct.h"
#include "hal.h"

#define CW_POWER_DDBM      40    /* +4.0 dBm, десяті частки */
#define CW_POWER_TOL_DDBM  15    /* ±1.5 dBm */
#define CW_SETTLE_US       2000u
#define RF_MEAS_TIMEOUT_US 100000u

#define XO_PPM_LIMIT       10
#define XO_MAX_STEPS       32

#define OTP_TRIM_SIGNATURE 0xCA5A0000u
#define OTP_VDDA_MIN_MV    3200
#define OTP_VDDA_MAX_MV    3400

static const uint32_t k_channels_khz[] = {2402000u, 2440000u, 2480000u};
#define CAL_CHANNEL_KHZ 2440000u

/* Код ємнісного масиву, знайдений тестом несучої; -1 — калібрування
 * не відпрацювало, писати в OTP нічого. */
static int32_t s_trim_found = -1;

static bool measure_channel(uint32_t freq_khz, hal_stand_rf_t *out)
{
    if (!hal_radio_cw_start(freq_khz, CW_POWER_DDBM)) {
        return false;
    }
    hal_delay_us(CW_SETTLE_US);
    bool ok = hal_stand_measure_rf(freq_khz, out, RF_MEAS_TIMEOUT_US);
    hal_radio_cw_stop();   /* несучу гасимо в будь-якому разі */
    return ok;
}

/* 1 ppm на 2440 МГц — це 2440 Гц. Ділимо з округленням до найближчого. */
static int32_t hz_to_ppm(int32_t error_hz, uint32_t freq_khz)
{
    int32_t per_ppm = (int32_t)(freq_khz / 1000u);
    int32_t half = per_ppm / 2;
    return error_hz >= 0 ? (error_hz + half) / per_ppm : (error_hz - half) / per_ppm;
}

static int32_t abs32(int32_t x)
{
    return x < 0 ? -x : x;
}

void test_rf_cw(fct_verdict_t *v)
{
    s_trim_found = -1;

    if (!hal_radio_init()) {
        fct_fail(v, FCT_FAIL, "Трансивер не ініціалізується");
        return;
    }

    /* 1. Потужність на нижньому, середньому й верхньому каналах. */
    const size_t count = sizeof(k_channels_khz) / sizeof(k_channels_khz[0]);
    int32_t worst_dev = 0;
    for (size_t i = 0; i < count; i++) {
        hal_stand_rf_t meas;
        if (!measure_channel(k_channels_khz[i], &meas)) {
            fct_fail_at(v, FCT_TIMEOUT, "Вимірювач стенда не відповів",
                        (int32_t)(k_channels_khz[i] / 1000u), "MHz");
            return;
        }
        int32_t dev = abs32((int32_t)meas.power_ddbm - CW_POWER_DDBM);
        if (dev > worst_dev) {
            worst_dev = dev;
        }
        if (dev > CW_POWER_TOL_DDBM) {
            fct_fail_at(v, FCT_FAIL,
                        "P_out поза ±1.5 dBm: балун, фільтр або імпеданс доріжки",
                        meas.power_ddbm, "ddBm");
            return;
        }
        hal_watchdog_kick();
    }

    /* 2. Підстроювання кварцу. Ємність масиву тягне частоту вниз, тому
     * додатне відхилення лікуємо збільшенням коду, від'ємне — зменшенням. */
    uint8_t trim = hal_radio_xo_trim();
    uint8_t best_trim = trim;
    int32_t best_ppm = INT32_MAX;
    int32_t prev_ppm = 0;
    bool have_prev = false;

    for (int step = 0; step < XO_MAX_STEPS; step++) {
        hal_radio_xo_trim_set(trim);

        hal_stand_rf_t meas;
        if (!measure_channel(CAL_CHANNEL_KHZ, &meas)) {
            fct_fail(v, FCT_TIMEOUT, "Стенд не віддав частоту піку");
            return;
        }
        int32_t ppm = hz_to_ppm(meas.freq_error_hz, CAL_CHANNEL_KHZ);
        if (abs32(ppm) < abs32(best_ppm)) {
            best_ppm = ppm;
            best_trim = trim;
        }
        if (abs32(ppm) <= XO_PPM_LIMIT) {
            break;
        }
        /* Знак перескочив — сусідні коди вже по різні боки нуля,
         * далі крокувати немає куди. */
        if (have_prev && ((ppm > 0) != (prev_ppm > 0))) {
            break;
        }
        if (ppm > 0) {
            if (trim >= HAL_XO_TRIM_MAX) {
                break;
            }
            trim++;
        } else {
            if (trim == 0) {
                break;
            }
            trim--;
        }
        prev_ppm = ppm;
        have_prev = true;
        hal_watchdog_kick();
    }

    hal_radio_xo_trim_set(best_trim);

    if (abs32(best_ppm) > XO_PPM_LIMIT) {
        fct_fail_at(v, FCT_FAIL, "Кварц не заганяється в ±10 ppm", best_ppm, "ppm");
        return;
    }

    s_trim_found = (int32_t)best_trim;
    fct_pass(v, "Несуча в допуску, кварц підстроєний", best_ppm, "ppm");
}

void test_otp_trim(fct_verdict_t *v)
{
    if (s_trim_found < 0) {
        fct_fail(v, FCT_SKIPPED, "Немає калібрувального коду — писати нічого");
        return;
    }

    const uint32_t trim = (uint32_t)s_trim_found & 0x3Fu;
    /* Слово несе код і його доповнення: напівпропалений біт видно одразу. */
    const uint32_t word = OTP_TRIM_SIGNATURE | (trim << 8) | ((~trim) & 0x3Fu);

    uint32_t stored = 0;
    if (!hal_otp_read(HAL_OTP_WORD_XO_TRIM, &stored)) {
        fct_fail(v, FCT_FAIL, "OTP: слово не читається");
        return;
    }
    if (stored != 0) {
        /* Плата вже проходила стенд: перепалити не можна, лише звірити. */
        if (stored != word) {
            fct_fail_at(v, FCT_INVALID_ID, "OTP уже містить інший код",
                        (int32_t)((stored >> 8) & 0x3Fu), "trim");
            return;
        }
        fct_pass(v, "OTP уже пропалений тим самим кодом", (int32_t)trim, "trim");
        return;
    }

    int32_t vdda_mv = 0;
    if (!fct_read_vdda_mv(&vdda_mv)) {
        fct_fail(v, FCT_TIMEOUT, "Перед записом OTP не вдалося зміряти V_DDA");
        return;
    }
    if (vdda_mv < OTP_VDDA_MIN_MV || vdda_mv > OTP_VDDA_MAX_MV) {
        fct_fail_at(v, FCT_FAIL, "V_DDA поза вікном пропалювання", vdda_mv, "mV");
        return;
    }

    if (!hal_otp_write(HAL_OTP_WORD_XO_TRIM, word)) {
        fct_fail(v, FCT_FAIL, "OTP: контролер відмовив у записі");
        return;
    }

    /* Просідання під час імпульсу 200 мА лишає біт напівпропаленим:
     * дефект випливе вже в полі, тому напругу міряємо ще й після запису. */
    if (!fct_read_vdda_mv(&vdda_mv)) {
        fct_fail(v, FCT_TIMEOUT, "Після запису OTP не вдалося зміряти V_DDA");
        return;
    }
    if (vdda_mv < OTP_VDDA_MIN_MV) {
        fct_fail_at(v, FCT_FAIL, "V_DDA просіла під час пропалювання",
                    vdda_mv, "mV");
        return;
    }

    uint32_t readback = 0;
    if (!hal_otp_read(HAL_OTP_WORD_XO_TRIM, &readback) || readback != word) {
        fct_fail(v, FCT_FAIL, "OTP: зчитане слово не збіглося із записаним");
        return;
    }

    fct_pass(v, "Код підстроювання пропалений і звірений", (int32_t)trim, "trim");
}
