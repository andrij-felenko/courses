#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define AS7341_I2C_ADDR         0x39

/* Регістри керування AS7341 */
#define AS7341_REG_ENABLE       0x80
#define AS7341_REG_ATIME        0x81
#define AS7341_REG_ASTEP_L      0xCA
#define AS7341_REG_ASTEP_H      0xCB
#define AS7341_REG_CFG_1        0xAA
#define AS7341_REG_STATUS       0x71
#define AS7341_REG_CH0_DATA_L   0x95

/* Структура 11 каналів сенсора AS7341 */
typedef struct {
    uint16_t f1_415nm;
    uint16_t f2_445nm;
    uint16_t f3_480nm;
    uint16_t f4_515nm;
    uint16_t f5_555nm;
    uint16_t f6_590nm;
    uint16_t f7_630nm;
    uint16_t f8_680nm;
    uint16_t clear;
    uint16_t nir;
    uint8_t  flicker_freq_hz;
} as7341_raw_data_t;

/* Результати спектрального аналізу */
typedef struct {
    float x;
    float y;
    float cct_kelvin;
    float lux;
    float cri_ra;
    float spd_mw_m2_nm[8];  /* Спектральна густина для 8 смуг */
} as7341_spectral_result_t;

/* Обчислення колірної температури за формулою МакКамі */
static float calculate_cct_mccamy(float x, float y) {
    if (fabsf(0.1858f - y) < 1e-5f) return 0.0f;
    float n = (x - 0.3320f) / (0.1858f - y);
    float n2 = n * n;
    float n3 = n2 * n;
    return 449.0f * n3 + 3525.0f * n2 + 6823.3f * n + 5520.33f;
}

/* Наближений розрахунок CRI Ra за 8 спектральними смугами */
static float estimate_cri_ra(const float spd[8], float cct) {
    /* Базове порівняння енергії в червоній (F7, F8) та синьо-зеленій зоні */
    float blue_sum = spd[0] + spd[1] + spd[2];
    float green_sum = spd[3] + spd[4];
    float red_sum = spd[5] + spd[6] + spd[7];
    float total = blue_sum + green_sum + red_sum;

    if (total < 1e-4f) return 0.0f;

    /* Штраф за спектральні провали відносно гладкого теплового спектра */
    float r_ratio = red_sum / total;
    float g_ratio = green_sum / total;
    float b_ratio = blue_sum / total;

    /* Для теплого світла < 4000 K брак червоного (R9/F7/F8) різко знижує CRI */
    float penalty = 0.0f;
    if (cct < 3500.0f && r_ratio < 0.35f) {
        penalty += (0.35f - r_ratio) * 150.0f;
    }
    if (g_ratio > 0.55f) { /* Типовий пік дешевих люмінесцентних ламп 546 нм */
        penalty += (g_ratio - 0.55f) * 120.0f;
    }

    float ra = 100.0f - penalty;
    if (ra > 100.0f) ra = 100.0f;
    if (ra < 0.0f) ra = 0.0f;
    return ra;
}

/* Повний конвеєр обробки сирих даних AS7341 */
void as7341_process_spectrum(const as7341_raw_data_t *raw, float atime_ms, float gain, as7341_spectral_result_t *res) {
    float norm_factor = (atime_ms * gain > 0.0f) ? (1.0f / (atime_ms * gain)) : 1.0f;

    /* Коефіцієнти калібрування каналів (відгук у мкВт/см²/відлік) */
    const float cal[8] = { 0.12f, 0.10f, 0.09f, 0.085f, 0.080f, 0.075f, 0.070f, 0.082f };

    res->spd_mw_m2_nm[0] = (float)raw->f1_415nm * norm_factor * cal[0];
    res->spd_mw_m2_nm[1] = (float)raw->f2_445nm * norm_factor * cal[1];
    res->spd_mw_m2_nm[2] = (float)raw->f3_480nm * norm_factor * cal[2];
    res->spd_mw_m2_nm[3] = (float)raw->f4_515nm * norm_factor * cal[3];
    res->spd_mw_m2_nm[4] = (float)raw->f5_555nm * norm_factor * cal[4];
    res->spd_mw_m2_nm[5] = (float)raw->f6_590nm * norm_factor * cal[5];
    res->spd_mw_m2_nm[6] = (float)raw->f7_630nm * norm_factor * cal[6];
    res->spd_mw_m2_nm[7] = (float)raw->f8_680nm * norm_factor * cal[7];

    /* Матрична згортка у координати CIE 1931 XYZ (матриця чутливості 3x8) */
    float X = 0.05f * res->spd_mw_m2_nm[0] + 0.35f * res->spd_mw_m2_nm[1] + 0.15f * res->spd_mw_m2_nm[2] +
              0.02f * res->spd_mw_m2_nm[3] + 0.30f * res->spd_mw_m2_nm[4] + 0.85f * res->spd_mw_m2_nm[5] +
              1.05f * res->spd_mw_m2_nm[6] + 0.35f * res->spd_mw_m2_nm[7];

    float Y = 0.01f * res->spd_mw_m2_nm[0] + 0.05f * res->spd_mw_m2_nm[1] + 0.14f * res->spd_mw_m2_nm[2] +
              0.55f * res->spd_mw_m2_nm[3] + 0.98f * res->spd_mw_m2_nm[4] + 0.75f * res->spd_mw_m2_nm[5] +
              0.25f * res->spd_mw_m2_nm[6] + 0.02f * res->spd_mw_m2_nm[7];

    float Z = 0.95f * res->spd_mw_m2_nm[0] + 1.85f * res->spd_mw_m2_nm[1] + 0.85f * res->spd_mw_m2_nm[2] +
              0.05f * res->spd_mw_m2_nm[3];

    float sum = X + Y + Z;
    if (sum > 1e-4f) {
        res->x = X / sum;
        res->y = Y / sum;
    } else {
        res->x = 0.3127f;
        res->y = 0.3290f;
    }

    res->lux = 683.0f * Y;
    res->cct_kelvin = calculate_cct_mccamy(res->x, res->y);
    res->cri_ra = estimate_cri_ra(res->spd_mw_m2_nm, res->cct_kelvin);
}
