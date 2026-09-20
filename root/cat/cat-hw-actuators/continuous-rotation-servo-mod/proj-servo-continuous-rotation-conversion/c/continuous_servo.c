/**
 * @file continuous_servo.c
 * @brief Реалізація процедурного драйвера сервопривода постійного обертання (C99).
 *
 * Інкапсулює алгоритми програмного калібрування нейтралі, кусково-лінійного
 * масштабування нормованої швидкості в тривалість імпульсу ШІМ з компенсацією
 * мертвої зони (deadband) та неблокувального лінійного рампінгу швидкості.
 */

#include "continuous_servo.h"
#include <math.h>
#include <string.h>

/**
 * @brief Допоміжна функція обмеження числа з рухомою комою у діапазоні [min_val, max_val]
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
 * @brief Розрахунок ефективної тривалості нейтрального імпульсу з урахуванням зсуву калібрування
 *
 * Ефективна тривалість формується як сума базової нейтралі (1500 мкс) та відносного зсуву,
 * після чого перевіряється на входження у безпечні межі [min_pulse + deadband, max_pulse - deadband].
 */
static inline uint16_t calculate_effective_neutral(const continuous_servo_calib_t *calib)
{
    int32_t eff = (int32_t)calib->neutral_pulse_us + calib->trim_offset_us;
    int32_t safe_min = (int32_t)calib->min_pulse_us + (int32_t)calib->deadband_us;
    int32_t safe_max = (int32_t)calib->max_pulse_us - (int32_t)calib->deadband_us;

    if (eff < safe_min) {
        eff = safe_min;
    } else if (eff > safe_max) {
        eff = safe_max;
    }
    return (uint16_t)eff;
}

/**
 * @brief Кусково-лінійне масштабування нормованої швидкості в тривалість імпульсу ШІМ
 *
 * Реалізує дві ключові вимоги:
 * 1. Гарантоване відсікання в зоні спокою: якщо модуль швидкості менший або дорівнює
 *    ramp->deadband_speed, повертається точне значення ефективної нейтралі. Внутрішній
 *    компаратор сервопривода бачить нульову різницю напруг, H-міст повністю вимикається,
 *    що усуває самочинне прокручування (creeping) та дрижання/гудіння (jitter/buzzing).
 * 2. Усунення мертвого ходу регулятора: при виході з мертвої зони тривалість імпульсу
 *    стартує відразу з межі апаратної мертвої зони (effective_neutral +/- deadband_us)
 *    і лінійно наростає до крайніх меж (min_pulse / max_pulse). Це забезпечує плавний пуск
 *    на мінімальних обертах без «провалу» в керуванні.
 *
 * @param servo Покажчик на дескриптор приводу.
 * @param speed Поточна нормована швидкість [-1.0f .. +1.0f].
 * @return Тривалість імпульсу ШІМ у мікросекундах.
 */
static uint16_t speed_to_pulse_us(const continuous_servo_t *servo, float speed)
{
    const continuous_servo_calib_t *calib = &servo->calib;
    const continuous_servo_ramp_t  *ramp  = &servo->ramp;

    uint16_t effective_neutral = calculate_effective_neutral(calib);
    uint16_t db = calib->deadband_us;

    /* 1. Відсікання швидкості в програмній мертвій зоні */
    if (fabsf(speed) <= ramp->deadband_speed) {
        return effective_neutral;
    }

    float pulse;
    if (speed > 0.0f) {
        /*
         * Пряме обертання (speed > deadband_speed):
         * Нормуємо швидкість на інтервал (0.0 .. 1.0]:
         *   speed_norm = (speed - deadband_speed) / (1.0f - deadband_speed)
         */
        float speed_norm = (speed - ramp->deadband_speed) / (1.0f - ramp->deadband_speed);
        if (speed_norm > 1.0f) {
            speed_norm = 1.0f;
        }

        /* Доступний діапазон ШІМ від межі мертвої зони до максимуму */
        float span_fwd = (float)calib->max_pulse_us - (float)(effective_neutral + db);
        pulse = (float)(effective_neutral + db) + speed_norm * span_fwd;
    } else {
        /*
         * Зворотне обертання (speed < -deadband_speed):
         * Нормуємо абсолютне значення швидкості:
         *   speed_norm = (-speed - deadband_speed) / (1.0f - deadband_speed)
         */
        float speed_norm = (-speed - ramp->deadband_speed) / (1.0f - ramp->deadband_speed);
        if (speed_norm > 1.0f) {
            speed_norm = 1.0f;
        }

        /* Доступний діапазон ШІМ від межі мертвої зони до мінімуму */
        float span_rev = (float)(effective_neutral - db) - (float)calib->min_pulse_us;
        pulse = (float)(effective_neutral - db) - speed_norm * span_rev;
    }

    /* Апаратне безпечне обмеження абсолютними межами (clamping) */
    if (pulse < (float)calib->min_pulse_us) {
        pulse = (float)calib->min_pulse_us;
    } else if (pulse > (float)calib->max_pulse_us) {
        pulse = (float)calib->max_pulse_us;
    }

    return (uint16_t)(pulse + 0.5f);
}

bool continuous_servo_init(continuous_servo_t *servo, const continuous_servo_config_t *config)
{
    if (servo == NULL || config == NULL || config->pwm_write == NULL) {
        return false;
    }

    /* Валідація фізичних часових меж ШІМ */
    if (config->calib.min_pulse_us < 400U || config->calib.max_pulse_us > 3000U ||
        config->calib.min_pulse_us >= config->calib.max_pulse_us) {
        return false;
    }

    /* Нейтраль повинна лежати суворо між мінімумом і максимумом */
    if (config->calib.neutral_pulse_us <= config->calib.min_pulse_us ||
        config->calib.neutral_pulse_us >= config->calib.max_pulse_us) {
        return false;
    }

    /* Мертва зона повинна залишати достатній робочий діапазон з обох боків */
    uint32_t min_span_left = (uint32_t)config->calib.neutral_pulse_us - config->calib.min_pulse_us;
    uint32_t min_span_right = (uint32_t)config->calib.max_pulse_us - config->calib.neutral_pulse_us;
    if ((uint32_t)config->calib.deadband_us * 2U >= min_span_left ||
        (uint32_t)config->calib.deadband_us * 2U >= min_span_right) {
        return false;
    }

    /* Валідація темпів лінійного прискорення та гальмування */
    if (config->ramp.accel_rate <= 0.0f || config->ramp.decel_rate <= 0.0f ||
        config->ramp.deadband_speed < 0.0f || config->ramp.deadband_speed >= 0.5f) {
        return false;
    }

    /* Копіювання конфігураційних параметрів */
    servo->calib = config->calib;
    servo->ramp = config->ramp;
    servo->pwm_write = config->pwm_write;
    servo->user_data = config->user_data;

    /* Ініціалізація динамічного стану приводу */
    servo->target_speed = 0.0f;
    servo->current_speed = 0.0f;
    servo->state = CONTINUOUS_SERVO_STATE_STOPPED;
    servo->initialized = true;

    /* Обчислення початкового нейтрального імпульсу спокою */
    servo->current_pulse_us = calculate_effective_neutral(&servo->calib);

    /* Негайне оновлення апаратного таймера нейтральним сигналом */
    servo->pwm_write(servo->current_pulse_us, servo->user_data);

    return true;
}

bool continuous_servo_calibrate_neutral(continuous_servo_t *servo, uint16_t measured_neutral_us)
{
    if (servo == NULL || !servo->initialized) {
        return false;
    }

    /* Перевіряємо, чи виміряна тривалість не виходить за допустимі межі безпеки */
    uint16_t safe_min = servo->calib.min_pulse_us + servo->calib.deadband_us;
    uint16_t safe_max = servo->calib.max_pulse_us - servo->calib.deadband_us;
    if (measured_neutral_us <= safe_min || measured_neutral_us >= safe_max) {
        return false;
    }

    /* Розраховуємо програмний зсув відносно номінальної нейтралі */
    servo->calib.trim_offset_us = (int16_t)((int32_t)measured_neutral_us - (int32_t)servo->calib.neutral_pulse_us);

    /* Якщо сервопривід зараз зупинений, негайно коригуємо імпульс на виході таймера */
    if (servo->state == CONTINUOUS_SERVO_STATE_STOPPED) {
        servo->current_pulse_us = calculate_effective_neutral(&servo->calib);
        if (servo->pwm_write != NULL) {
            servo->pwm_write(servo->current_pulse_us, servo->user_data);
        }
    }

    return true;
}

bool continuous_servo_set_neutral_trim(continuous_servo_t *servo, int16_t trim_us)
{
    if (servo == NULL || !servo->initialized) {
        return false;
    }

    int32_t effective = (int32_t)servo->calib.neutral_pulse_us + trim_us;
    int32_t safe_min = (int32_t)servo->calib.min_pulse_us + (int32_t)servo->calib.deadband_us;
    int32_t safe_max = (int32_t)servo->calib.max_pulse_us - (int32_t)servo->calib.deadband_us;

    if (effective <= safe_min || effective >= safe_max) {
        return false;
    }

    servo->calib.trim_offset_us = trim_us;

    if (servo->state == CONTINUOUS_SERVO_STATE_STOPPED) {
        servo->current_pulse_us = calculate_effective_neutral(&servo->calib);
        if (servo->pwm_write != NULL) {
            servo->pwm_write(servo->current_pulse_us, servo->user_data);
        }
    }

    return true;
}

int16_t continuous_servo_get_neutral_trim(const continuous_servo_t *servo)
{
    if (servo == NULL) {
        return 0;
    }
    return servo->calib.trim_offset_us;
}

uint16_t continuous_servo_get_effective_neutral(const continuous_servo_t *servo)
{
    if (servo == NULL) {
        return CONTINUOUS_SERVO_DEFAULT_NEUTRAL_US;
    }
    return calculate_effective_neutral(&servo->calib);
}

void continuous_servo_set_speed(continuous_servo_t *servo, float speed)
{
    if (servo == NULL || !servo->initialized) {
        return;
    }
    servo->target_speed = clamp_float(speed, -1.0f, 1.0f);
}

void continuous_servo_set_speed_immediate(continuous_servo_t *servo, float speed)
{
    if (servo == NULL || !servo->initialized) {
        return;
    }

    float clamped_speed = clamp_float(speed, -1.0f, 1.0f);
    servo->target_speed = clamped_speed;
    servo->current_speed = clamped_speed;

    if (fabsf(clamped_speed) <= servo->ramp.deadband_speed) {
        servo->state = CONTINUOUS_SERVO_STATE_STOPPED;
    } else {
        servo->state = CONTINUOUS_SERVO_STATE_CRUISING;
    }

    uint16_t pulse = speed_to_pulse_us(servo, clamped_speed);
    servo->current_pulse_us = pulse;

    if (servo->pwm_write != NULL) {
        servo->pwm_write(pulse, servo->user_data);
    }
}

void continuous_servo_stop(continuous_servo_t *servo)
{
    continuous_servo_set_speed(servo, 0.0f);
}

void continuous_servo_emergency_stop(continuous_servo_t *servo)
{
    if (servo == NULL || !servo->initialized) {
        return;
    }

    servo->target_speed = 0.0f;
    servo->current_speed = 0.0f;
    servo->state = CONTINUOUS_SERVO_STATE_STOPPED;

    uint16_t pulse = calculate_effective_neutral(&servo->calib);
    servo->current_pulse_us = pulse;

    if (servo->pwm_write != NULL) {
        servo->pwm_write(pulse, servo->user_data);
    }
}

void continuous_servo_update(continuous_servo_t *servo, uint32_t dt_ms)
{
    if (servo == NULL || !servo->initialized || dt_ms == 0) {
        return;
    }

    float dt_s = (float)dt_ms / 1000.0f;
    float diff = servo->target_speed - servo->current_speed;

    /* Перевірка досягнення цільової швидкості з урахуванням похибки float */
    if (fabsf(diff) < 1e-4f) {
        servo->current_speed = servo->target_speed;
        if (fabsf(servo->current_speed) <= servo->ramp.deadband_speed) {
            servo->state = CONTINUOUS_SERVO_STATE_STOPPED;
        } else {
            servo->state = CONTINUOUS_SERVO_STATE_CRUISING;
        }
    } else {
        /*
         * Вибір темпу зміни швидкості та визначення поточного динамічного стану:
         * 1. Реверс: знаки поточної та цільової швидкостей протилежні.
         *    Для збереження шестерень редуктора та уникнення сплеску струму проти-ЕРС
         *    привід спочатку інтенсивно гальмує до нуля (темп decel_rate).
         * 2. Гальмування: модуль цільової швидкості менший за поточну в тому ж напрямку.
         * 3. Розгін (софт-старт): нарощування модуля швидкості з обмеженням accel_rate.
         */
        float rate;
        if ((servo->current_speed > 0.0f && servo->target_speed < 0.0f) ||
            (servo->current_speed < 0.0f && servo->target_speed > 0.0f)) {
            servo->state = CONTINUOUS_SERVO_STATE_REVERSING;
            rate = servo->ramp.decel_rate;
        } else if (fabsf(servo->target_speed) < fabsf(servo->current_speed)) {
            servo->state = CONTINUOUS_SERVO_STATE_DECEL;
            rate = servo->ramp.decel_rate;
        } else {
            servo->state = CONTINUOUS_SERVO_STATE_ACCEL;
            rate = servo->ramp.accel_rate;
        }

        float max_step = rate * dt_s;
        if (fabsf(diff) <= max_step) {
            servo->current_speed = servo->target_speed;
            if (fabsf(servo->current_speed) <= servo->ramp.deadband_speed) {
                servo->state = CONTINUOUS_SERVO_STATE_STOPPED;
            } else {
                servo->state = CONTINUOUS_SERVO_STATE_CRUISING;
            }
        } else {
            if (diff > 0.0f) {
                servo->current_speed += max_step;
            } else {
                servo->current_speed -= max_step;
            }
        }
    }

    /* Кусково-лінійне масштабування швидкості в тривалість імпульсу ШІМ */
    uint16_t pulse = speed_to_pulse_us(servo, servo->current_speed);
    servo->current_pulse_us = pulse;

    /* Оновлення регістра апаратного таймера мікроконтролера */
    if (servo->pwm_write != NULL) {
        servo->pwm_write(pulse, servo->user_data);
    }
}

float continuous_servo_get_target_speed(const continuous_servo_t *servo)
{
    if (servo == NULL) {
        return 0.0f;
    }
    return servo->target_speed;
}

float continuous_servo_get_current_speed(const continuous_servo_t *servo)
{
    if (servo == NULL) {
        return 0.0f;
    }
    return servo->current_speed;
}

uint16_t continuous_servo_get_pulse_us(const continuous_servo_t *servo)
{
    if (servo == NULL) {
        return CONTINUOUS_SERVO_DEFAULT_NEUTRAL_US;
    }
    return servo->current_pulse_us;
}

continuous_servo_state_t continuous_servo_get_state(const continuous_servo_t *servo)
{
    if (servo == NULL) {
        return CONTINUOUS_SERVO_STATE_STOPPED;
    }
    return servo->state;
}

continuous_servo_direction_t continuous_servo_get_direction(const continuous_servo_t *servo)
{
    if (servo == NULL || !servo->initialized) {
        return CONTINUOUS_SERVO_DIR_STOP;
    }

    if (servo->current_speed > servo->ramp.deadband_speed) {
        return CONTINUOUS_SERVO_DIR_FORWARD;
    }
    if (servo->current_speed < -servo->ramp.deadband_speed) {
        return CONTINUOUS_SERVO_DIR_REVERSE;
    }
    return CONTINUOUS_SERVO_DIR_STOP;
}

bool continuous_servo_is_target_reached(const continuous_servo_t *servo)
{
    if (servo == NULL || !servo->initialized) {
        return true;
    }
    return (fabsf(servo->current_speed - servo->target_speed) < 1e-4f);
}

const char *continuous_servo_state_name(continuous_servo_state_t state)
{
    switch (state) {
    case CONTINUOUS_SERVO_STATE_STOPPED:
        return "СТОП (НЕЙТРАЛЬ)";
    case CONTINUOUS_SERVO_STATE_ACCEL:
        return "РОЗГІН (SOFT-START)";
    case CONTINUOUS_SERVO_STATE_CRUISING:
        return "СТАЛИЙ РУХ";
    case CONTINUOUS_SERVO_STATE_DECEL:
        return "ГАЛЬМУВАННЯ";
    case CONTINUOUS_SERVO_STATE_REVERSING:
        return "РЕВЕРС ЧЕРЕЗ 0";
    default:
        return "НЕВІДОМИЙ СТАН";
    }
}
