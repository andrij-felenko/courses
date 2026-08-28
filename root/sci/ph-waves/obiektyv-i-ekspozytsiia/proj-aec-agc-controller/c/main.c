#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define AEC_GRID_COLS 8
#define AEC_GRID_ROWS 8

typedef enum {
    AEC_FLICKER_OFF = 0,
    AEC_FLICKER_50HZ = 50,
    AEC_FLICKER_60HZ = 60
} aec_flicker_mode_t;

typedef struct {
    /* Конфігураційні ліміти */
    uint32_t min_exposure_us;
    uint32_t max_exposure_us;
    uint32_t max_motion_exposure_us; /* Ліміт витримки для запобігання Motion Blur */
    float min_analog_gain;
    float max_analog_gain;
    float min_digital_gain;
    float max_digital_gain;

    /* Параметри регулятора */
    float target_luma;               /* Цільова середня яскравість (зазвичай 118.0) */
    float deadband_luma;             /* Зона нечутливості (зазвичай 3.0) */
    float kp;                        /* Пропорційний коефіцієнт демпфування (0.2 - 0.5) */
    aec_flicker_mode_t flicker_mode; /* Режим захисту від мерехтіння */

    /* Поточний стан сенсора */
    uint32_t current_exposure_us;
    float current_analog_gain;
    float current_digital_gain;
} aec_controller_t;

/* Вагова матриця 8x8 (Center-Weighted Gaussian Mask) */
static const uint8_t g_center_weights[AEC_GRID_ROWS][AEC_GRID_COLS] = {
    { 1,  1,  2,  2,  2,  2,  1,  1 },
    { 1,  2,  4,  4,  4,  4,  2,  1 },
    { 2,  4,  8, 12, 12,  8,  4,  2 },
    { 2,  4, 12, 16, 16, 12,  4,  2 },
    { 2,  4, 12, 16, 16, 12,  4,  2 },
    { 2,  4,  8, 12, 12,  8,  4,  2 },
    { 1,  2,  4,  4,  4,  4,  2,  1 },
    { 1,  1,  2,  2,  2,  2,  1,  1 }
};

void aec_init(aec_controller_t *ctrl) {
    if (!ctrl) return;

    ctrl->min_exposure_us = 50;           /* 1/20000 с */
    ctrl->max_exposure_us = 33333;        /* 1/30 с */
    ctrl->max_motion_exposure_us = 8333;  /* 1/120 с */
    ctrl->min_analog_gain = 1.0f;
    ctrl->max_analog_gain = 16.0f;
    ctrl->min_digital_gain = 1.0f;
    ctrl->max_digital_gain = 4.0f;

    ctrl->target_luma = 118.0f;           /* 18% сіра карта при гаммі 2.2 */
    ctrl->deadband_luma = 3.0f;
    ctrl->kp = 0.35f;
    ctrl->flicker_mode = AEC_FLICKER_50HZ;

    ctrl->current_exposure_us = 10000;
    ctrl->current_analog_gain = 1.0f;
    ctrl->current_digital_gain = 1.0f;
}

float aec_compute_weighted_luma(const uint8_t grid_luma[AEC_GRID_ROWS][AEC_GRID_COLS]) {
    uint32_t weighted_sum = 0;
    uint32_t total_weight = 0;

    for (int r = 0; r < AEC_GRID_ROWS; ++r) {
        for (int c = 0; c < AEC_GRID_COLS; ++c) {
            uint32_t w = g_center_weights[r][c];
            weighted_sum += (uint32_t)grid_luma[r][c] * w;
            total_weight += w;
        }
    }

    if (total_weight == 0) return 1.0f;
    return (float)weighted_sum / (float)total_weight;
}

static uint32_t aec_apply_antiflicker(uint32_t exp_us, aec_flicker_mode_t mode, uint32_t min_exp, uint32_t max_exp) {
    if (mode == AEC_FLICKER_OFF) return exp_us;

    uint32_t step_us = (mode == AEC_FLICKER_50HZ) ? 10000 : 8333;

    if (exp_us < step_us) {
        return exp_us; /* При надкоротких витримках Anti-Flicker не застосовується */
    }

    /* Квантування до найближчого кроку періоду мережі */
    uint32_t steps = (exp_us + (step_us / 2)) / step_us;
    if (steps == 0) steps = 1;

    uint32_t quantized = steps * step_us;
    if (quantized < min_exp) quantized = min_exp;
    if (quantized > max_exp) quantized = max_exp;

    return quantized;
}

bool aec_update(aec_controller_t *ctrl, float measured_luma) {
    if (!ctrl) return false;

    if (measured_luma < 1.0f) measured_luma = 1.0f;

    float error = ctrl->target_luma - measured_luma;

    /* Перевірка зони нечутливості (Deadband) */
    if (fabsf(error) <= ctrl->deadband_luma) {
        return false; /* Параметри стабільні, коригування не потрібне */
    }

    /* Логарифмічний розрахунок зсуву експозиційного числа EV */
    float luma_ratio = ctrl->target_luma / measured_luma;
    float delta_ev = ctrl->kp * (logf(luma_ratio) / 0.693147f); /* log2(x) = ln(x)/ln(2) */

    /* Обмеження максимальної швидкості зміни за один кадр (максимум +-1.5 EV) */
    if (delta_ev > 1.5f) delta_ev = 1.5f;
    if (delta_ev < -1.5f) delta_ev = -1.5f;

    float exposure_scale = exp2f(delta_ev);

    /* Сумарний фотометричний ресурс */
    float current_total = (float)ctrl->current_exposure_us *
                          ctrl->current_analog_gain *
                          ctrl->current_digital_gain;

    float desired_total = current_total * exposure_scale;

    /* Пріоритетний розподіл: 1) Shutter -> 2) Analog Gain -> 3) Digital Gain */
    uint32_t target_exp = ctrl->min_exposure_us;
    float target_ana_gain = ctrl->min_analog_gain;
    float target_dig_gain = ctrl->min_digital_gain;

    float budget = desired_total;

    /* Фаза 1: Керування витримкою при одиничному підсиленні */
    float max_shutter_budget = (float)ctrl->max_motion_exposure_us * ctrl->min_analog_gain * ctrl->min_digital_gain;

    if (budget <= max_shutter_budget) {
        target_exp = (uint32_t)(budget / (ctrl->min_analog_gain * ctrl->min_digital_gain));
        target_ana_gain = ctrl->min_analog_gain;
        target_dig_gain = ctrl->min_digital_gain;
    } else {
        /* Витримка досягла порогу захисту від змазу */
        target_exp = ctrl->max_motion_exposure_us;
        budget /= (float)target_exp;

        /* Фаза 2: Нарощування аналогового підсилення */
        if (budget <= ctrl->max_analog_gain) {
            target_ana_gain = budget;
            target_dig_gain = ctrl->min_digital_gain;
        } else {
            /* Аналогове підсилення досягло максимуму */
            target_ana_gain = ctrl->max_analog_gain;
            budget /= target_ana_gain;

            /* Фаза 3: Цифрове підсилення */
            if (budget <= ctrl->max_digital_gain) {
                target_dig_gain = budget;
            } else {
                /* Екстремальна темрява: подовження витримки понад ліміт руху */
                target_dig_gain = ctrl->max_digital_gain;
                float remaining = budget / ctrl->max_digital_gain;
                uint32_t extended_exp = (uint32_t)((float)target_exp * remaining);
                if (extended_exp > ctrl->max_exposure_us) extended_exp = ctrl->max_exposure_us;
                target_exp = extended_exp;
            }
        }
    }

    /* Застосування фільтра Anti-Flicker */
    target_exp = aec_apply_antiflicker(target_exp, ctrl->flicker_mode,
                                       ctrl->min_exposure_us, ctrl->max_exposure_us);

    /* Апаратне обмеження меж */
    if (target_exp < ctrl->min_exposure_us) target_exp = ctrl->min_exposure_us;
    if (target_exp > ctrl->max_exposure_us) target_exp = ctrl->max_exposure_us;
    if (target_ana_gain < ctrl->min_analog_gain) target_ana_gain = ctrl->min_analog_gain;
    if (target_ana_gain > ctrl->max_analog_gain) target_ana_gain = ctrl->max_analog_gain;
    if (target_dig_gain < ctrl->min_digital_gain) target_dig_gain = ctrl->min_digital_gain;
    if (target_dig_gain > ctrl->max_digital_gain) target_dig_gain = ctrl->max_digital_gain;

    ctrl->current_exposure_us = target_exp;
    ctrl->current_analog_gain = target_ana_gain;
    ctrl->current_digital_gain = target_dig_gain;

    return true;
}
