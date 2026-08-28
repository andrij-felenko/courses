/* uvi_calculator.h / uvi_calculator.c
 * Промисловий модуль розрахунку міжнародного УФ-індексу та оптичної компенсації.
 */

#ifndef UVI_CALCULATOR_H
#define UVI_CALCULATOR_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Категорії ризику УФ-випромінювання за класифікацією WHO */
typedef enum {
    UVI_RISK_LOW = 0,        /* UVI 0.0 .. 2.9  (Зелений)     */
    UVI_RISK_MODERATE,       /* UVI 3.0 .. 5.9  (Жовтий)      */
    UVI_RISK_HIGH,           /* UVI 6.0 .. 7.9  (Помаранчевий) */
    UVI_RISK_VERY_HIGH,      /* UVI 8.0 .. 10.9 (Червоний)     */
    UVI_RISK_EXTREME         /* UVI 11.0+       (Фіолетовий)   */
} uvi_risk_level_t;

/* Фототипи шкіри за шкалою Фіцпатріка (Fitzpatrick Phototypes I - VI) */
typedef enum {
    SKIN_TYPE_I = 1,  /* Кельтський: дуже світла шкіра, 1 MED ≈ 200 Дж/м² */
    SKIN_TYPE_II,     /* Скандинавський: світла шкіра, 1 MED ≈ 250 Дж/м²  */
    SKIN_TYPE_III,    /* Середньоєвропейський: 1 MED ≈ 350 Дж/м²          */
    SKIN_TYPE_IV,     /* Середземноморський: 1 MED ≈ 450 Дж/м²            */
    SKIN_TYPE_V,      /* Азійський/індійський: 1 MED ≈ 600 Дж/м²          */
    SKIN_TYPE_VI      /* Африканський: 1 MED ≈ 1000 Дж/м²                 */
} skin_phototype_t;

/* Сирі відліки 16-бітного АЦП від чотириканального кремнієвого сенсора */
typedef struct {
    uint16_t raw_uva;   /* Канал з фільтром UV-A */
    uint16_t raw_uvb;   /* Канал з фільтром UV-B */
    uint16_t raw_vis;   /* Канал видимого світла (компенсаційний) */
    uint16_t raw_ir;    /* Канал інфрачервоного фону (компенсаційний) */
} uvi_raw_data_t;

/* Матричні калібрувальні коефіцієнти перехресного оптичного засвічення */
typedef struct {
    float uva_a_vis;       /* Коефіцієнт проникнення видимого світла в UV-A (a) */
    float uva_b_ir;        /* Коефіцієнт проникнення ІЧ світла в UV-A (b)        */
    float uvb_c_vis;       /* Коефіцієнт проникнення видимого світла в UV-B (c) */
    float uvb_d_ir;        /* Коефіцієнт проникнення ІЧ світла в UV-B (d)        */
    float uva_offset;      /* Темновий зсув каналу UV-A (counts)                 */
    float uvb_offset;      /* Темновий зсув каналу UV-B (counts)                 */
    float uva_responsivity;/* Еритемний ваговий коефіцієнт k_A (UVI / counts)    */
    float uvb_responsivity;/* Еритемний ваговий коефіцієнт k_B (UVI / counts)    */
} uvi_calibration_t;

/* Результат повного розрахунку */
typedef struct {
    float uva_compensated;    /* Очищений потік UV-A (умовні одиниці / counts) */
    float uvb_compensated;    /* Очищений потік UV-B (умовні одиниці / counts) */
    float uv_index;            /* Міжнародний УФ-індекс (UVI, безрозмірний)     */
    float erythemal_power_wm2; /* Ефективна еритемна опроміненість (Вт/м²)      */
    uvi_risk_level_t risk;     /* Рівень загрози за класифікацією WHO           */
    uint32_t burn_time_sec;    /* Безпечний час експозиції до опіку (секунди)   */
} uvi_result_t;

/* Функція ініціалізації типових калібрувальних коефіцієнтів (для AM1.5G) */
void uvi_get_default_calibration(uvi_calibration_t *calib);

/* Функція обробки даних, компенсації та обчислення індексу */
bool uvi_calculate(const uvi_raw_data_t *raw,
                   const uvi_calibration_t *calib,
                   skin_phototype_t skin,
                   uvi_result_t *out_result);

/* Отримання текстового опису ризику за ВООЗ */
const char* uvi_risk_to_string(uvi_risk_level_t risk);

#ifdef __cplusplus
}
#endif

#endif /* UVI_CALCULATOR_H */

/* ── Реалізація алгоритму ─────────────────────────────────────────────────── */

void uvi_get_default_calibration(uvi_calibration_t *calib) {
    if (!calib) return;
    /* Типові коефіцієнти матриці для 4-канальних кремнієвих сенсорів */
    calib->uva_a_vis = 2.22f;
    calib->uva_b_ir  = 2.12f;
    calib->uvb_c_vis = 2.95f;
    calib->uvb_d_ir  = 1.74f;
    calib->uva_offset = 0.0f;
    calib->uvb_offset = 0.0f;
    /* Чутливість: перевод кількості відліків в одиниці UVI */
    calib->uva_responsivity = 0.001461f;
    calib->uvb_responsivity = 0.002591f;
}

const char* uvi_risk_to_string(uvi_risk_level_t risk) {
    switch (risk) {
        case UVI_RISK_LOW:       return "Низький (Low): захист не потрібен";
        case UVI_RISK_MODERATE:  return "Помірний (Moderate): рекомендовано захист";
        case UVI_RISK_HIGH:      return "Високий (High): захист обов'язковий";
        case UVI_RISK_VERY_HIGH: return "Дуже високий (Very High): перебувайте в затінку";
        case UVI_RISK_EXTREME:   return "Екстремальний (Extreme): уникайте сонця";
        default:                 return "Невідомий";
    }
}

static uint32_t get_med_joules(skin_phototype_t skin) {
    switch (skin) {
        case SKIN_TYPE_I:   return 200;
        case SKIN_TYPE_II:  return 250;
        case SKIN_TYPE_III: return 350;
        case SKIN_TYPE_IV:  return 450;
        case SKIN_TYPE_V:   return 600;
        case SKIN_TYPE_VI:  return 1000;
        default:            return 250;
    }
}

bool uvi_calculate(const uvi_raw_data_t *raw,
                   const uvi_calibration_t *calib,
                   skin_phototype_t skin,
                   uvi_result_t *out_result)
{
    if (!raw || !calib || !out_result) {
        return false;
    }

    /* Крок 1. Матрична компенсація оптичного проникнення видимого та ІЧ світла */
    float vis = (float)raw->raw_vis;
    float ir  = (float)raw->raw_ir;

    float comp_uva = (float)raw->raw_uva - (calib->uva_a_vis * vis)
                                         - (calib->uva_b_ir * ir)
                                         - calib->uva_offset;

    float comp_uvb = (float)raw->raw_uvb - (calib->uvb_c_vis * vis)
                                         - (calib->uvb_d_ir * ir)
                                         - calib->uvb_offset;

    /* Фізичне обмеження: сигнал не може бути від'ємним через похибки квантування */
    if (comp_uva < 0.0f) comp_uva = 0.0f;
    if (comp_uvb < 0.0f) comp_uvb = 0.0f;

    /* Крок 2. Обчислення зваженого еритемного УФ-індексу */
    float uvi_a = comp_uva * calib->uva_responsivity;
    float uvi_b = comp_uvb * calib->uvb_responsivity;
    float total_uvi = (uvi_a + uvi_b) / 2.0f;

    if (total_uvi < 0.0f) total_uvi = 0.0f;

    out_result->uva_compensated = comp_uva;
    out_result->uvb_compensated = comp_uvb;
    out_result->uv_index = total_uvi;

    /* Крок 3. Еритемна ефективна потужність: 1 UVI = 0.025 Вт/м² = 25 мВт/м² */
    out_result->erythemal_power_wm2 = total_uvi * 0.025f;

    /* Крок 4. Класифікація рівня небезпеки за шкалою ВООЗ */
    if (total_uvi < 3.0f) {
        out_result->risk = UVI_RISK_LOW;
    } else if (total_uvi < 6.0f) {
        out_result->risk = UVI_RISK_MODERATE;
    } else if (total_uvi < 8.0f) {
        out_result->risk = UVI_RISK_HIGH;
    } else if (total_uvi < 11.0f) {
        out_result->risk = UVI_RISK_VERY_HIGH;
    } else {
        out_result->risk = UVI_RISK_EXTREME;
    }

    /* Крок 5. Розрахунок часу до появи сонячного опіку (MED / E_er) */
    uint32_t med_dose = get_med_joules(skin);
    if (out_result->erythemal_power_wm2 > 0.0001f) {
        float sec = (float)med_dose / out_result->erythemal_power_wm2;
        out_result->burn_time_sec = (sec > 86400.0f) ? 86400U : (uint32_t)sec;
    } else {
        out_result->burn_time_sec = 86400U; /* Понад добу (безпечно) */
    }

    return true;
}
