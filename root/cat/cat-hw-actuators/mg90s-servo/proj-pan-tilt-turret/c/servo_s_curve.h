#ifndef SERVO_S_CURVE_H
#define SERVO_S_CURVE_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Стандартні фізичні та часові межі сервопривода MG90S V2:
 *  - Робочий діапазон вала: 0..180 градусів
 *  - Тривалість імпульсу ШІМ: 500..2400 мкс (період 20 мс, частота 50 Гц)
 *  - Рекомендований крок квантування планувальника: 10 мс (100 Гц)
 */
#define SERVO_DEFAULT_MIN_ANGLE_DEG   0
#define SERVO_DEFAULT_MAX_ANGLE_DEG   180
#define SERVO_DEFAULT_MIN_PULSE_US    500
#define SERVO_DEFAULT_MAX_PULSE_US    2400
#define SERVO_DEFAULT_DT_MS           10

/*
 * Цілочисельна арифметика фіксованої точки Q16.16:
 *  - 16 бітів для цілої частини зі знаком (-32768 .. +32767)
 *  - 16 бітів для дробової частини (дискретність 1/65536 ~ 0.000015)
 */
typedef int32_t q16_t;

#define Q16_SHIFT             16
#define Q16_ONE               ((q16_t)(1 << Q16_SHIFT))
#define Q16_HALF              ((q16_t)(1 << (Q16_SHIFT - 1)))

#define Q16_FROM_INT(v)       ((q16_t)((int32_t)(v) << Q16_SHIFT))
#define Q16_TO_INT(v)         ((int32_t)((v) >> Q16_SHIFT))
#define Q16_TO_INT_ROUND(v)   ((int32_t)(((v) + Q16_HALF) >> Q16_SHIFT))

/* Базові математичні макроси та інлайн-функції для Q16.16 */
static inline q16_t q16_mul(q16_t a, q16_t b) {
    return (q16_t)(((int64_t)a * b) >> Q16_SHIFT);
}

static inline q16_t q16_div(q16_t a, q16_t b) {
    if (b == 0) {
        return 0;
    }
    return (q16_t)((((int64_t)a) << Q16_SHIFT) / b);
}

static inline q16_t q16_abs(q16_t a) {
    return (a < 0) ? -a : a;
}

/*
 * Обчислення цілочисельного квадратного кореня у форматі Q16.16 без FPU.
 * Використовує детермінований бінарний алгоритм порозрядного обчислення.
 */
static inline q16_t q16_sqrt(q16_t x) {
    if (x <= 0) {
        return 0;
    }
    uint64_t val = ((uint64_t)x) << Q16_SHIFT;
    uint64_t temp, g = 0;
    uint64_t b = 0x4000000000000000ULL;
    while (b > 0) {
        temp = g + b;
        g >>= 1;
        if (val >= temp) {
            val -= temp;
            g += b;
        }
        b >>= 2;
    }
    return (q16_t)g;
}

/*
 * Контекст сервопривода.
 * Повністю позбавлений динамічної пам'яті (malloc/free).
 * Екземпляри виділяються клієнтом статично або на стеку (~56 байт на привід).
 */
typedef struct {
    /* Калібрувальні кутові межі (градуси у форматі Q16.16) */
    q16_t min_angle_deg_q16;
    q16_t max_angle_deg_q16;

    /* Калібрувальні межі ШІМ для гарантованого захисту від кінцевих упорів */
    uint16_t min_pulse_us;
    uint16_t max_pulse_us;

    /* Динамічні обмеження кінематики (Q16.16) */
    q16_t max_vel_deg_s;      /* Максимальна швидкість (град/с) */
    q16_t max_accel_deg_s2;   /* Максимальне прискорення (град/с^2) */

    /* Крок квантування часу планувальника (мілісекунди) */
    uint16_t dt_ms;

    /* Поточний розрахований стан (Q16.16) */
    q16_t current_pos_q16;    /* Поточний кут (град) */
    q16_t current_vel_q16;    /* Поточна швидкість (град/с) */
    q16_t current_acc_q16;    /* Поточне прискорення (град/с^2) */

    /* Параметри поточної траєкторії руху */
    q16_t start_pos_q16;      /* Початковий кут відрізка */
    q16_t target_pos_q16;     /* Цільовий кут відрізка */
    q16_t duration_q16;       /* Розрахована тривалість руху (секунди у Q16.16) */
    uint32_t total_steps;     /* Загальна кількість дискретних кроків */
    uint32_t current_step;    /* Поточний крок траєкторії (0..total_steps) */
    bool is_moving;           /* Прапорець активного виконання профілю */

    /* Розрахована вихідна тривалість імпульсу ШІМ з апаратним clamping */
    uint16_t current_pulse_us;
} servo_s_curve_t;

/* Ініціалізація структури за замовчуванням (0..180 град, 500..2400 мкс) */
void servo_s_curve_init(servo_s_curve_t *servo, uint16_t dt_ms, q16_t initial_angle_deg_q16);

/* Налаштування калібрувальних меж для захисту редуктора */
void servo_s_curve_set_limits(servo_s_curve_t *servo,
                              q16_t min_angle_q16,
                              q16_t max_angle_q16,
                              uint16_t min_pulse_us,
                              uint16_t max_pulse_us);

/* Налаштування динамічних лімітів швидкості та прискорення */
void servo_s_curve_set_motion_profile(servo_s_curve_t *servo,
                                      q16_t max_vel_deg_s,
                                      q16_t max_accel_deg_s2);

/*
 * Запуск плавного руху до цільового кута з автоматичним розрахунком
 * тривалості за обмеженнями max_vel та max_accel.
 */
bool servo_s_curve_set_target(servo_s_curve_t *servo, q16_t target_angle_deg_q16);

/* Запуск руху до цільового кута з явно заданою фіксованою тривалістю (мс) */
bool servo_s_curve_set_target_duration(servo_s_curve_t *servo,
                                       q16_t target_angle_deg_q16,
                                       uint32_t duration_ms);

/*
 * Неблокуючий крок оновлення траєкторії.
 * Викликається раз на dt_ms із таймерного переривання (ISR) або суперциклу.
 * Повертає true, якщо рух триває, або false, якщо ціль досягнуто.
 */
bool servo_s_curve_update(servo_s_curve_t *servo);

/* Отримання поточної тривалості імпульсу ШІМ (мкс) для запису в регістр таймера */
uint16_t servo_s_curve_get_pulse_us(const servo_s_curve_t *servo);

/* Отримання поточного кута у форматі Q16.16 (градуси) */
q16_t servo_s_curve_get_angle_q16(const servo_s_curve_t *servo);

/* Отримання поточної швидкості у форматі Q16.16 (град/с) */
q16_t servo_s_curve_get_velocity_q16(const servo_s_curve_t *servo);

/* Отримання поточного прискорення у форматі Q16.16 (град/с^2) */
q16_t servo_s_curve_get_accel_q16(const servo_s_curve_t *servo);

/* Перевірка стану руху */
bool servo_s_curve_is_moving(const servo_s_curve_t *servo);

/*
 * Функція конвертації кута в тривалість імпульсу ШІМ із подвійним clamping:
 * як за межами кута, так і за абсолютними мікросекундами.
 */
uint16_t servo_s_curve_angle_to_pulse(const servo_s_curve_t *servo, q16_t angle_deg_q16);

#ifdef __cplusplus
}
#endif

#endif /* SERVO_S_CURVE_H */
