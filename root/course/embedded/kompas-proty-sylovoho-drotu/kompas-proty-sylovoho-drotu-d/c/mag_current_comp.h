/* mag_current_comp.h - C99 Implementation */
#ifndef MAG_CURRENT_COMP_H
#define MAG_CURRENT_COMP_H

#include <stdbool.h>
#include <math.h>

typedef struct {
    float k[3];             /* Вектор коефіцієнтів [kx, ky, kz] у мкТл/А */
    float current_lpf;      /* Стан фільтра низьких частот струму */
    float lpf_alpha;        /* Коефіцієнт IIR фільтра: alpha = dt / (RC + dt) */
    float max_allowed_curr; /* Захисний поріг валідності струму */
    bool  is_active;        /* Прапорець дозволу компенсації */
} mag_current_comp_t;

/**
 * Ініціалізація структури компенсатора
 * @param comp Покажчик на структуру
 * @param kx, ky, kz Розраховані коефіцієнти регресії
 * @param dt_sec Період виклику функції (наприклад, 0.01с для 100 Гц)
 * @param cutoff_hz Частота зрізу узгоджувального фільтра (типово 12–15 Гц)
 */
static inline void mag_current_comp_init(mag_current_comp_t *comp,
                                        float kx, float ky, float kz,
                                        float dt_sec, float cutoff_hz) {
    comp->k[0] = kx;
    comp->k[1] = ky;
    comp->k[2] = kz;
    comp->current_lpf = 0.0f;
    comp->max_allowed_curr = 250.0f; /* Відсікання аномальних викидів сенсора струму */

    float rc = 1.0f / (2.0f * 3.14159265f * cutoff_hz);
    comp->lpf_alpha = dt_sec / (rc + dt_sec);

    /* Активуємо лише якщо бодай один коефіцієнт ненульовий */
    float norm_sq = kx*kx + ky*ky + kz*kz;
    comp->is_active = (norm_sq > 1e-6f);
}

/**
 * Потокова корекція тривісного вектора магнітометра
 * @param comp Покажчик на структуру
 * @param raw_current_amps Миттєвий вимір струму від Power Module
 * @param mag_uncomp Вхідний вектор [Bx, By, Bz] у мкТл після Hard/Soft Iron
 * @param mag_comp Вихідний очищений вектор [Bx, By, Bz]
 */
static inline void mag_current_comp_process(mag_current_comp_t *comp,
                                            float raw_current_amps,
                                            const float mag_uncomp[3],
                                            float mag_comp[3]) {
    if (!comp->is_active || raw_current_amps < 0.0f || raw_current_amps > comp->max_allowed_curr) {
        mag_comp[0] = mag_uncomp[0];
        mag_comp[1] = mag_uncomp[1];
        mag_comp[2] = mag_uncomp[2];
        return;
    }

    /* Фільтрація струму для збігу фази з буфером магнітометра */
    comp->current_lpf += comp->lpf_alpha * (raw_current_amps - comp->current_lpf);

    /* Векторне віднімання динамічної струмової завади */
    mag_comp[0] = mag_uncomp[0] - comp->k[0] * comp->current_lpf;
    mag_comp[1] = mag_uncomp[1] - comp->k[1] * comp->current_lpf;
    mag_comp[2] = mag_uncomp[2] - comp->k[2] * comp->current_lpf;
}

#endif /* MAG_CURRENT_COMP_H */
