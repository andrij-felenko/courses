/* cg_adaptive_mixer.h / cg_adaptive_mixer.c
 * Вбудований адаптивний мікшер для 4-роторної X-рами зі зсувом CG
 */

#include <math.h>
#include <stdbool.h>
#include <string.h>

#define NUM_MOTORS 4

typedef struct {
    float arm_length_x;    /* Базове плече X від центру рами, м */
    float arm_length_y;    /* Базове плече Y від центру рами, м */
    float k_thrust;        /* Коефіцієнт тяги, Н / (норм. одиниця тяги) */
    float k_torque;        /* Коефіцієнт реактивного моменту, Н·м / Н */
    float mass_total;      /* Повна маса апарата, кг */
    float gravity;         /* Прискорення вільного падіння, м/с² */
    float est_alpha;       /* Коефіцієнт згладжування оцінювача (dt / tau) */
    float max_cg_offset_x; /* Максимально допустимий зсув X, м */
    float max_cg_offset_y; /* Максимально допустимий зсув Y, м */
} CgMixerConfig;

typedef struct {
    float offset_x;        /* Оцінене зміщення CG по X (ніс/хвіст), м */
    float offset_y;        /* Оцінене зміщення CG по Y (борт), м */
    float motor_thrusts[NUM_MOTORS]; /* Тяга кожного мотора [0.0 ... 1.0] */
    bool  is_saturated;    /* Прапорець насичення моторів */
} CgMixerState;

/* Ініціалізація стану мікшера */
void cg_mixer_init(CgMixerState *state) {
    if (!state) return;
    state->offset_x = 0.0f;
    state->offset_y = 0.0f;
    state->is_saturated = false;
    for (int i = 0; i < NUM_MOTORS; ++i) {
        state->motor_thrusts[i] = 0.0f;
    }
}

/* Оновлення оцінки положення CG на основі тривалого дисбалансу тяги */
void cg_estimator_update(const CgMixerConfig *cfg, CgMixerState *state,
                         bool in_steady_hover, float dt) {
    if (!cfg || !state || !in_steady_hover) return;

    /* Використовуємо поточний розподіл тяги для виявлення статичного моменту:
     * Мотори: 0 = Передній-Правий (CW),  1 = Задній-Лівий (CW),
     *         2 = Передній-Лівий (CCW), 3 = Задній-Правий (CCW)
     */
    float t_front = state->motor_thrusts[0] + state->motor_thrusts[2];
    float t_rear  = state->motor_thrusts[1] + state->motor_thrusts[3];
    float t_right = state->motor_thrusts[0] + state->motor_thrusts[3];
    float t_left  = state->motor_thrusts[1] + state->motor_thrusts[2];

    float total_t = t_front + t_rear;
    if (total_t < 0.2f) return; /* Апарат не у повітрі */

    /* Розрахунок миттєвого плеча з умови рівноваги сил */
    float raw_dx = cfg->arm_length_x * (t_rear - t_front) / total_t;
    float raw_dy = cfg->arm_length_y * (t_left - t_right) / total_t;

    /* Низькочастотна фільтрація оцінки */
    float alpha = cfg->est_alpha * dt;
    if (alpha > 1.0f) alpha = 1.0f;

    state->offset_x += alpha * (raw_dx - state->offset_x);
    state->offset_y += alpha * (raw_dy - state->offset_y);

    /* Обмеження безпеки */
    if (state->offset_x > cfg->max_cg_offset_x) state->offset_x = cfg->max_cg_offset_x;
    if (state->offset_x < -cfg->max_cg_offset_x) state->offset_x = -cfg->max_cg_offset_x;
    if (state->offset_y > cfg->max_cg_offset_y) state->offset_y = cfg->max_cg_offset_y;
    if (state->offset_y < -cfg->max_cg_offset_y) state->offset_y = -cfg->max_cg_offset_y;
}

/* Розрахунок тяги моторів з динамічною компенсацією геометрії */
void cg_mixer_compute(const CgMixerConfig *cfg, CgMixerState *state,
                      float thrust_cmd, float roll_torque, float pitch_torque, float yaw_torque) {
    if (!cfg || !state) return;

    /* Миттєві скориговані плечі кожного з чотирьох моторів відносно оціненого CG */
    /* Мотор 0: Передній-Правий (+X_arm, +Y_arm) */
    float lx0 = cfg->arm_length_x - state->offset_x;
    float ly0 = cfg->arm_length_y - state->offset_y;

    /* Мотор 1: Задній-Лівий (-X_arm, -Y_arm) */
    float lx1 = cfg->arm_length_x + state->offset_x;
    float ly1 = cfg->arm_length_y + state->offset_y;

    /* Мотор 2: Передній-Лівий (+X_arm, -Y_arm) */
    float lx2 = cfg->arm_length_x - state->offset_x;
    float ly2 = cfg->arm_length_y + state->offset_y;

    /* Мотор 3: Задній-Правий (-X_arm, +Y_arm) */
    float lx3 = cfg->arm_length_x + state->offset_x;
    float ly3 = cfg->arm_length_y - state->offset_y;

    /* Геометричний перерахунок матриці розподілу (диференціальні добавки) */
    float r_roll  = roll_torque  / (4.0f * cfg->k_thrust * cfg->arm_length_y);
    float r_pitch = pitch_torque / (4.0f * cfg->k_thrust * cfg->arm_length_x);
    float r_yaw   = yaw_torque   / (4.0f * cfg->k_thrust * cfg->k_torque);

    /* Базова тяга з урахуванням статичного вирівнювання CG */
    float base_t = thrust_cmd * 0.25f;

    /* Розрахунок індивідуальних команд для моторів X-конфігурації */
    float t[NUM_MOTORS];
    t[0] = base_t * (lx1 / (lx0 + lx1)) * (ly1 / (ly0 + ly1)) * 4.0f - r_roll + r_pitch - r_yaw;
    t[1] = base_t * (lx0 / (lx0 + lx1)) * (ly0 / (ly0 + ly1)) * 4.0f + r_roll - r_pitch - r_yaw;
    t[2] = base_t * (lx1 / (lx0 + lx1)) * (ly0 / (ly0 + ly1)) * 4.0f + r_roll + r_pitch + r_yaw;
    t[3] = base_t * (lx0 / (lx0 + lx1)) * (ly1 / (ly0 + ly1)) * 4.0f - r_roll - r_pitch + r_yaw;

    /* Захист від насичення (Desaturation) з пріоритетом стабілізації кутів */
    float min_t = t[0], max_t = t[0];
    for (int i = 1; i < NUM_MOTORS; ++i) {
        if (t[i] < min_t) min_t = t[i];
        if (t[i] > max_t) max_t = t[i];
    }

    state->is_saturated = false;

    if (max_t > 1.0f) {
        float shift = max_t - 1.0f;
        for (int i = 0; i < NUM_MOTORS; ++i) {
            t[i] -= shift; /* Знижуємо загальну тягу, зберігаючи моменти */
        }
        state->is_saturated = true;
    }

    if (min_t < 0.0f) {
        for (int i = 0; i < NUM_MOTORS; ++i) {
            if (t[i] < 0.0f) t[i] = 0.0f;
        }
        state->is_saturated = true;
    }

    /* Запис результату */
    for (int i = 0; i < NUM_MOTORS; ++i) {
        if (t[i] > 1.0f) t[i] = 1.0f;
        state->motor_thrusts[i] = t[i];
    }
}
