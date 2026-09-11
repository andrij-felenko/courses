#ifndef SERVO_DRIVER_H
#define SERVO_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Статуси виконання операцій драйвера сервопривода.
 */
typedef enum {
    SERVO_OK = 0,               ///< Успішне виконання
    SERVO_ERR_INVALID_ARG = 1,  ///< Передано некоректний покажчик або невалідний аргумент
    SERVO_ERR_OUT_OF_RANGE = 2, ///< Значення виходить за межі допустимого діапазону
    SERVO_ERR_NOT_ATTACHED = 3  ///< Операція неможлива: генерація ШІМ вимкнена
} servo_status_t;

/**
 * @brief Тип покажчика на функцію запису ширини імпульсу в регістр таймера.
 * @param timer_instance Покажчик на базову адресу регістрів таймера.
 * @param channel Номер апаратного каналу.
 * @param pulse_us Тривалість активного імпульсу в мікросекундах.
 */
typedef void (*servo_hal_write_pulse_fn)(void *timer_instance, uint32_t channel, uint16_t pulse_us);

/**
 * @brief Тип покажчика на функцію ввімкнення/вимкнення генерації ШІМ на каналі.
 * @param timer_instance Покажчик на регістри таймера.
 * @param channel Номер апаратного каналу.
 * @param enable true — увімкнути генерацію, false — вимкнути (Hi-Z / низький рівень).
 */
typedef void (*servo_hal_set_enabled_fn)(void *timer_instance, uint32_t channel, bool enable);

/**
 * @brief Структура апаратних колбеків для переносимості між платформами (HAL).
 */
typedef struct {
    servo_hal_write_pulse_fn write_pulse;
    servo_hal_set_enabled_fn set_enabled;
} servo_hal_ops_t;

/**
 * @brief Повний дескриптор екземпляра сервопривода.
 */
typedef struct {
    // Апаратна прив'язка
    void *timer_instance;
    uint32_t channel;
    servo_hal_write_pulse_fn hal_write_pulse;
    servo_hal_set_enabled_fn hal_set_pwm_enabled;

    // Калібрувальні параметри
    uint16_t min_pulse_us;
    uint16_t max_pulse_us;
    float max_angle_deg;

    // Динамічний стан позиціонування
    float current_angle_deg;
    float target_angle_deg;
    float speed_deg_per_s;      ///< Максимальна швидкість повороту (град/с)
    uint16_t current_pulse_us;
    bool is_attached;
} servo_t;

/**
 * @brief Ініціалізація дескриптора сервопривода з параметрами калібрування.
 */
servo_status_t servo_init(servo_t *servo,
                          void *timer_instance,
                          uint32_t channel,
                          const servo_hal_ops_t *ops,
                          uint16_t min_pulse_us,
                          uint16_t max_pulse_us,
                          float max_angle_deg);

/**
 * @brief Активація генерації імпульсів ШІМ на каналі таймера.
 */
servo_status_t servo_attach(servo_t *servo);

/**
 * @brief Деактивація генерації імпульсів ШІМ для знеструмлення мотора.
 */
servo_status_t servo_detach(servo_t *servo);

/**
 * @brief Безпосереднє встановлення кута без обмеження швидкості.
 */
servo_status_t servo_write_angle(servo_t *servo, float angle_deg);

/**
 * @brief Безпосередній запис тривалості імпульсу в мікросекундах.
 */
servo_status_t servo_write_microseconds(servo_t *servo, uint16_t pulse_us);

/**
 * @brief Завдання цільового кута та швидкості переміщення для плавного руху.
 */
servo_status_t servo_set_target_angle(servo_t *servo, float target_angle_deg, float speed_deg_per_s);

/**
 * @brief Періодичний крок оновлення координати (slew-rate limiter).
 */
bool servo_update(servo_t *servo, uint32_t dt_ms);

#ifdef __cplusplus
}
#endif

#endif // SERVO_DRIVER_H
