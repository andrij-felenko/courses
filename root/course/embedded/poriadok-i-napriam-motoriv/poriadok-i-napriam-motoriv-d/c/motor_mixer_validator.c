/* ============================================================================
 * motor_mixer_validator.c — Модуль валідації мікшера та реакцій гіроскопа (C99)
 * ============================================================================ */
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define MAX_MOTORS 8

typedef enum {
    SPIN_DIR_CCW =  1, /* Проти годинникової стрілки */
    SPIN_DIR_CW  = -1  /* За годинниковою стрілкою */
} SpinDirection;

typedef enum {
    VAL_OK = 0,
    VAL_ERR_ROLL_SIGN_MISMATCH  = (1 << 0),
    VAL_ERR_PITCH_SIGN_MISMATCH = (1 << 1),
    VAL_ERR_YAW_SIGN_MISMATCH   = (1 << 2),
    VAL_ERR_THRUST_UNBALANCED   = (1 << 3),
    VAL_ERR_YAW_TORQUE_IMBALANCE= (1 << 4)
} ValidationResult;

typedef struct {
    float x;             /* Відстань від центру мас вперед (+X, м) */
    float y;             /* Відстань від центру мас праворуч (+Y, м) */
    SpinDirection spin;  /* Напрямок обертання ротора */
} MotorGeometry;

typedef struct {
    float roll;
    float pitch;
    float yaw;
    float throttle;
} MotorMixEntry;

typedef struct {
    uint8_t motor_count;
    MotorGeometry geometry[MAX_MOTORS];
    MotorMixEntry mixer[MAX_MOTORS];
} DroneFrameConfig;

/* Валідація коректності знаків мікшування та балансу реактивних сил */
ValidationResult validate_motor_mixer(const DroneFrameConfig *cfg) {
    ValidationResult res = VAL_OK;
    float total_yaw_bias = 0.0f;
    float total_roll_sum = 0.0f;
    float total_pitch_sum = 0.0f;

    for (uint8_t i = 0; i < cfg->motor_count; i++) {
        const MotorGeometry *g = &cfg->geometry[i];
        const MotorMixEntry *m = &cfg->mixer[i];

        /* 1. Перевірка крену (Roll):
         * Мотор праворуч (y > 0) при додаванні газу накренює дрон ліворуч (-Roll).
         * Відповідно, для компенсації нахилу вправо мікшер для правого мотора
         * мусить мати від'ємний або додатний знак відповідно до конвенції знаків.
         * У системі координат NED: тяга правого мотора зменшує крен (знак мікшера < 0). */
        if (fabsf(g->y) > 0.01f) {
            float expected_roll_sign = (g->y > 0.0f) ? -1.0f : 1.0f;
            if ((m->roll * expected_roll_sign) < 0.0f) {
                res |= VAL_ERR_ROLL_SIGN_MISMATCH;
            }
        }

        /* 2. Перевірка тангажу (Pitch):
         * Мотор попереду (x > 0) при додаванні газу опускає ніс (-Pitch).
         * Команда підняття носа (+Pitch) вимагає зменшення тяги переднього мотора (знак < 0). */
        if (fabsf(g->x) > 0.01f) {
            float expected_pitch_sign = (g->x > 0.0f) ? -1.0f : 1.0f;
            if ((m->pitch * expected_pitch_sign) < 0.0f) {
                res |= VAL_ERR_PITCH_SIGN_MISMATCH;
            }
        }

        /* 3. Перевірка курсу (Yaw):
         * Мотор CCW (+1) створює реактивний момент розвороту праворуч (+Yaw).
         * Команда повороту праворуч (+Yaw) мусить розганяти мотор CCW (знак > 0). */
        float expected_yaw_sign = (g->spin == SPIN_DIR_CCW) ? 1.0f : -1.0f;
        if ((m->yaw * expected_yaw_sign) < 0.0f) {
            res |= VAL_ERR_YAW_SIGN_MISMATCH;
        }

        total_yaw_bias += (float)g->spin;
        total_roll_sum += m->roll;
        total_pitch_sum += m->pitch;
    }

    /* Симетрія перерозподілу моментів (сума коефіцієнтів поворотів має бути нульовою) */
    if (fabsf(total_roll_sum) > 0.01f || fabsf(total_pitch_sum) > 0.01f) {
        res |= VAL_ERR_THRUST_UNBALANCED;
    }

    /* Баланс реактивних моментів висіння (кількість CW повинна дорівнювати CCW) */
    if (fabsf(total_yaw_bias) > 0.01f) {
        res |= VAL_ERR_YAW_TORQUE_IMBALANCE;
    }

    return res;
}
