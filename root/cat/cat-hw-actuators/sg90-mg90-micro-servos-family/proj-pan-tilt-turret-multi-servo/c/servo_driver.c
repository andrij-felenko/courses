/**
 * @file servo_driver.c
 * @brief Реалізація модульного процедурного драйвера мікросервоприводів (C99).
 *
 * Відокремлює генерацію кінематичної траєкторії від безпосередньої взаємодії
 * з периферією мікроконтролера. Забезпечує детермінований розрахунок координати,
 * захисний клемпінг у зоні софт-лімітів та лінійну трансформацію в мікросекунди ШІМ.
 */

#include "servo_driver.h"
#include <math.h>
#include <string.h>

/**
 * @brief Допоміжна функція обмеження числа з рухомою комою в заданому діапазоні [min_val, max_val]
 */
static inline float clamp_float(float val, float min_val, float max_val)
{
    if (val < min_val) {
        return min_val;
    }
    if (val > max_val) {
        return max_val;
    }
    return val;
}

/**
 * @brief Розрахунок ефективної нейтралі з урахуванням калібрувального зсуву
 */
static inline uint16_t calculate_effective_neutral(const servo_calib_t *calib)
{
    int32_t eff = (int32_t)calib->neutral_pulse_us + calib->trim_offset_us;
    int32_t safe_min = (int32_t)calib->min_pulse_us + 100;
    int32_t safe_max = (int32_t)calib->max_pulse_us - 100;

    if (eff < safe_min) {
        eff = safe_min;
    } else if (eff > safe_max) {
        eff = safe_max;
    }
    return (uint16_t)eff;
}

uint16_t servo_angle_to_pulse_us(const servo_t *servo, float angle_deg)
{
    if (servo == NULL) {
        return SERVO_DEFAULT_NEUTRAL_US;
    }

    const servo_calib_t *calib = &servo->calib;
    float safe_angle = clamp_float(angle_deg, SERVO_PHYSICAL_MIN_ANGLE_DEG, SERVO_PHYSICAL_MAX_ANGLE_DEG);
    uint16_t eff_neutral = calculate_effective_neutral(calib);

    /*
     * Кусково-лінійна інтерполяція через калібровану точку нейтралі (90°):
     * Це гарантує, що при куті рівно 90.0° формується точний імпульс ефективної нейтралі,
     * а на краях 0° і 180° тривалість збігається з фізичними межами приводу без асиметрії.
     */
    float pulse;
    if (safe_angle <= SERVO_PHYSICAL_NEUTRAL_DEG) {
        /* Діапазон [0° .. 90°]: масштабування від min_pulse_us до eff_neutral */
        float norm = safe_angle / SERVO_PHYSICAL_NEUTRAL_DEG;
        pulse = (float)calib->min_pulse_us + norm * ((float)eff_neutral - (float)calib->min_pulse_us);
    } else {
        /* Діапазон [90° .. 180°]: масштабування від eff_neutral до max_pulse_us */
        float norm = (safe_angle - SERVO_PHYSICAL_NEUTRAL_DEG) /
                     (SERVO_PHYSICAL_MAX_ANGLE_DEG - SERVO_PHYSICAL_NEUTRAL_DEG);
        pulse = (float)eff_neutral + norm * ((float)calib->max_pulse_us - (float)eff_neutral);
    }

    /* Апаратний клемпінг для запобігання генерації неприпустимих імпульсів */
    if (pulse < (float)calib->min_pulse_us) {
        pulse = (float)calib->min_pulse_us;
    } else if (pulse > (float)calib->max_pulse_us) {
        pulse = (float)calib->max_pulse_us;
    }

    return (uint16_t)(pulse + 0.5f);
}

bool servo_init(servo_t *servo, const servo_config_t *config)
{
    if (servo == NULL || config == NULL || config->pwm_write == NULL) {
        return false;
    }

    /* Валідація фізичних часових меж ШІМ */
    if (config->calib.min_pulse_us < 400U || config->calib.max_pulse_us > 2700U ||
        config->calib.min_pulse_us >= config->calib.max_pulse_us) {
        return false;
    }

    /* Нейтраль повинна лежати строго між мінімумом і максимумом */
    if (config->calib.neutral_pulse_us <= config->calib.min_pulse_us ||
        config->calib.neutral_pulse_us >= config->calib.max_pulse_us) {
        return false;
    }

    /* Валідація програмних софт-лімітів кутів */
    if (config->limits.min_angle_deg < SERVO_PHYSICAL_MIN_ANGLE_DEG ||
        config->limits.max_angle_deg > SERVO_PHYSICAL_MAX_ANGLE_DEG ||
        config->limits.min_angle_deg >= config->limits.max_angle_deg) {
        return false;
    }

    /* Валідація кінематичних обмежень траєкторії */
    if (config->kinematics.max_velocity_deg_s <= 0.0f ||
        config->kinematics.max_accel_deg_s2 <= 0.0f) {
        return false;
    }

    /* Копіювання конфігураційних блоків у дескриптор приводу */
    servo->calib = config->calib;
    servo->limits = config->limits;
    servo->kinematics = config->kinematics;
    servo->pwm_write = config->pwm_write;
    servo->user_data = config->user_data;

    /* Початкове позиціювання вала з урахуванням софт-лімітів */
    float safe_initial = clamp_float(config->initial_angle_deg,
                                     servo->limits.min_angle_deg,
                                     servo->limits.max_angle_deg);

    servo->target_angle_deg = safe_initial;
    servo->current_angle_deg = safe_initial;
    servo->current_velocity_deg_s = 0.0f;
    servo->state = SERVO_STATE_IDLE;
    servo->initialized = true;

    /* Розрахунок первинного імпульсу та негайне оновлення апаратного таймера */
    servo->current_pulse_us = servo_angle_to_pulse_us(servo, safe_initial);
    servo->pwm_write(servo->current_pulse_us, servo->user_data);

    return true;
}

bool servo_set_target_angle(servo_t *servo, float angle_deg)
{
    if (servo == NULL || !servo->initialized) {
        return false;
    }

    /*
     * Софт-ліміти: захисне обмеження кутової координати.
     * Запобігає випадковому завданню небезпечних кутів, що призводять до упору
     * вала в механічні стопори, стрибка струму I_stall > 1.0 А та зрізання зубців редуктора.
     */
    float clamped_angle = clamp_float(angle_deg,
                                      servo->limits.min_angle_deg,
                                      servo->limits.max_angle_deg);

    servo->target_angle_deg = clamped_angle;

    /* Повертає true, якщо вхідне значення цілком відповідало дозволеному сектору */
    return (angle_deg == clamped_angle);
}

void servo_set_target_angle_immediate(servo_t *servo, float angle_deg)
{
    if (servo == NULL || !servo->initialized) {
        return;
    }

    float clamped_angle = clamp_float(angle_deg,
                                      servo->limits.min_angle_deg,
                                      servo->limits.max_angle_deg);

    servo->target_angle_deg = clamped_angle;
    servo->current_angle_deg = clamped_angle;
    servo->current_velocity_deg_s = 0.0f;
    servo->state = SERVO_STATE_IDLE;

    servo->current_pulse_us = servo_angle_to_pulse_us(servo, clamped_angle);
    if (servo->pwm_write != NULL) {
        servo->pwm_write(servo->current_pulse_us, servo->user_data);
    }
}

bool servo_set_neutral_trim(servo_t *servo, int16_t trim_offset_us)
{
    if (servo == NULL || !servo->initialized) {
        return false;
    }

    int32_t eff = (int32_t)servo->calib.neutral_pulse_us + trim_offset_us;
    int32_t safe_min = (int32_t)servo->calib.min_pulse_us + 100;
    int32_t safe_max = (int32_t)servo->calib.max_pulse_us - 100;

    if (eff <= safe_min || eff >= safe_max) {
        return false;
    }

    servo->calib.trim_offset_us = trim_offset_us;

    /* Якщо привід у стані спокою, негайно коригуємо імпульс у регістрі таймера */
    if (servo->state == SERVO_STATE_IDLE) {
        servo->current_pulse_us = servo_angle_to_pulse_us(servo, servo->current_angle_deg);
        if (servo->pwm_write != NULL) {
            servo->pwm_write(servo->current_pulse_us, servo->user_data);
        }
    }

    return true;
}

int16_t servo_get_neutral_trim(const servo_t *servo)
{
    if (servo == NULL) {
        return 0;
    }
    return servo->calib.trim_offset_us;
}

uint16_t servo_get_effective_neutral(const servo_t *servo)
{
    if (servo == NULL) {
        return SERVO_DEFAULT_NEUTRAL_US;
    }
    return calculate_effective_neutral(&servo->calib);
}

bool servo_set_soft_limits(servo_t *servo, float min_angle_deg, float max_angle_deg)
{
    if (servo == NULL || !servo->initialized) {
        return false;
    }

    if (min_angle_deg < SERVO_PHYSICAL_MIN_ANGLE_DEG ||
        max_angle_deg > SERVO_PHYSICAL_MAX_ANGLE_DEG ||
        min_angle_deg >= max_angle_deg) {
        return false;
    }

    servo->limits.min_angle_deg = min_angle_deg;
    servo->limits.max_angle_deg = max_angle_deg;

    /* Якщо поточна ціль опинилася за новими межами, коригуємо її */
    servo->target_angle_deg = clamp_float(servo->target_angle_deg, min_angle_deg, max_angle_deg);
    return true;
}

bool servo_set_kinematics(servo_t *servo, float max_velocity_deg_s, float max_accel_deg_s2)
{
    if (servo == NULL || !servo->initialized) {
        return false;
    }

    if (max_velocity_deg_s <= 0.0f || max_accel_deg_s2 <= 0.0f) {
        return false;
    }

    servo->kinematics.max_velocity_deg_s = max_velocity_deg_s;
    servo->kinematics.max_accel_deg_s2 = max_accel_deg_s2;
    return true;
}

void servo_update(servo_t *servo, uint32_t dt_ms)
{
    if (servo == NULL || !servo->initialized || dt_ms == 0) {
        return;
    }

    float dt_s = (float)dt_ms / 1000.0f;
    float dist = servo->target_angle_deg - servo->current_angle_deg;
    float abs_dist = fabsf(dist);

    const float EPSILON_ANGLE = 0.02f; /* Поріг завершення позиціювання (градуси) */

    /* Перевірка перебування в цільовій точці спокою */
    if (abs_dist <= EPSILON_ANGLE && fabsf(servo->current_velocity_deg_s) <= 0.2f) {
        servo->current_angle_deg = servo->target_angle_deg;
        servo->current_velocity_deg_s = 0.0f;
        servo->state = SERVO_STATE_IDLE;
    } else {
        /*
         * Генератор трапецеїдального профілю швидкості в дискретному часі:
         * 1. Розрахунок граничної безпечної швидкості гальмування v_stop за формулою Торрічеллі:
         *      v_stop = sqrt(2 * a_max * distance)
         *    Це гарантує, що привід почне гальмувати завчасно і зупиниться точно в цілі
         *    без перерегулювання (overshoot = 0%) та без удару об механічні упори.
         */
        float a_max = servo->kinematics.max_accel_deg_s2;
        float v_max = servo->kinematics.max_velocity_deg_s;
        float dir = (dist > 0.0f) ? 1.0f : -1.0f;

        float v_stop = sqrtf(2.0f * a_max * abs_dist);
        float v_limit = (v_max < v_stop) ? v_max : v_stop;
        float v_desired = dir * v_limit;

        /* 2. Обмеження темпу зміни швидкості максимальним прискоренням a_max */
        float dv_max = a_max * dt_s;
        float dv = v_desired - servo->current_velocity_deg_s;
        dv = clamp_float(dv, -dv_max, dv_max);

        float new_velocity = servo->current_velocity_deg_s + dv;
        new_velocity = clamp_float(new_velocity, -v_max, v_max);
        servo->current_velocity_deg_s = new_velocity;

        /* 3. Інтегрування кутової координати вала */
        float delta_angle = new_velocity * dt_s;

        /* Якщо залишковий шлях менший або дорівнює дискретному кроку — фіксуємо ціль */
        if (abs_dist <= fabsf(delta_angle) && (dir * new_velocity >= 0.0f)) {
            servo->current_angle_deg = servo->target_angle_deg;
            servo->current_velocity_deg_s = 0.0f;
            servo->state = SERVO_STATE_IDLE;
        } else {
            servo->current_angle_deg += delta_angle;

            /* Захисний клемпінг поточної позиції всередині дозволених софт-лімітів */
            servo->current_angle_deg = clamp_float(servo->current_angle_deg,
                                                   servo->limits.min_angle_deg,
                                                   servo->limits.max_angle_deg);

            /* 4. Класифікація поточного динамічного стану для діагностики */
            if (v_limit < (v_max - 0.5f) && (dir * servo->current_velocity_deg_s > 0.0f)) {
                servo->state = SERVO_STATE_DECEL;
            } else if (fabsf(servo->current_velocity_deg_s) >= (v_max - 1.0f)) {
                servo->state = SERVO_STATE_CRUISE;
            } else {
                servo->state = SERVO_STATE_ACCEL;
            }
        }
    }

    /* 5. Детермінований перерахунок кутової координати в мікросекунди ШІМ 50 Гц */
    uint16_t pulse = servo_angle_to_pulse_us(servo, servo->current_angle_deg);
    servo->current_pulse_us = pulse;

    /* 6. Оновлення регістра апаратного таймера мікроконтролера */
    if (servo->pwm_write != NULL) {
        servo->pwm_write(pulse, servo->user_data);
    }
}

void servo_emergency_stop(servo_t *servo)
{
    if (servo == NULL || !servo->initialized) {
        return;
    }

    servo->target_angle_deg = servo->current_angle_deg;
    servo->current_velocity_deg_s = 0.0f;
    servo->state = SERVO_STATE_IDLE;

    servo->current_pulse_us = servo_angle_to_pulse_us(servo, servo->current_angle_deg);
    if (servo->pwm_write != NULL) {
        servo->pwm_write(servo->current_pulse_us, servo->user_data);
    }
}

float servo_get_current_angle(const servo_t *servo)
{
    return (servo != NULL) ? servo->current_angle_deg : SERVO_PHYSICAL_NEUTRAL_DEG;
}

float servo_get_target_angle(const servo_t *servo)
{
    return (servo != NULL) ? servo->target_angle_deg : SERVO_PHYSICAL_NEUTRAL_DEG;
}

float servo_get_velocity(const servo_t *servo)
{
    return (servo != NULL) ? servo->current_velocity_deg_s : 0.0f;
}

uint16_t servo_get_pulse_us(const servo_t *servo)
{
    return (servo != NULL) ? servo->current_pulse_us : SERVO_DEFAULT_NEUTRAL_US;
}

servo_state_t servo_get_state(const servo_t *servo)
{
    return (servo != NULL) ? servo->state : SERVO_STATE_IDLE;
}

bool servo_is_target_reached(const servo_t *servo)
{
    if (servo == NULL || !servo->initialized) {
        return true;
    }
    return (servo->state == SERVO_STATE_IDLE);
}

const char *servo_state_name(servo_state_t state)
{
    switch (state) {
    case SERVO_STATE_IDLE:
        return "СПОКІЙ (ЦІЛЬ ДОСЯГНУТА)";
    case SERVO_STATE_ACCEL:
        return "РОЗГІН (ПЛАВНИЙ ПУСК)";
    case SERVO_STATE_CRUISE:
        return "КРЕЙСЕРСЬКИЙ ХІД";
    case SERVO_STATE_DECEL:
        return "ГАЛЬМУВАННЯ В ЦІЛЬ";
    default:
        return "НЕВІДОМИЙ СТАН";
    }
}
