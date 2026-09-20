#ifndef DRV8833_H
#define DRV8833_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file drv8833.h
 * @brief Заголовний файл драйвера двоканального H-моста DRV8833.
 *
 * Модуль забезпечує керування двома колекторними моторами постійного струму (канали A та B)
 * через входи IN1-IN4 із використанням апаратного ШІМ та логічних виходів GPIO.
 */

/* Значення для позначення невикористовуваного виводу або каналу */
#define DRV8833_PIN_UNUSED 0xFF

/**
 * @brief Ідентифікатор мотора DRV8833.
 */
typedef enum {
    DRV8833_MOTOR_A = 0, /* Мотор A (входи IN1, IN2) */
    DRV8833_MOTOR_B = 1  /* Мотор B (входи IN3, IN4) */
} drv8833_motor_id_t;

/**
 * @brief Режими руху та гальмування мотора.
 */
typedef enum {
    DRV8833_MODE_COAST = 0, /* Вільний вибіг (High-Z, входи LOW) */
    DRV8833_MODE_FORWARD,   /* Рух уперед (IN1 ШІМ, IN2 LOW) */
    DRV8833_MODE_REVERSE,   /* Рух назад (IN1 LOW, IN2 ШІМ) */
    DRV8833_MODE_BRAKE      /* Активне гальмування (Low-Z, входи HIGH) */
} drv8833_mode_t;

/**
 * @brief Коди результату виконання функцій драйвера.
 */
typedef enum {
    DRV8833_OK = 0,                /* Операція успішна */
    DRV8833_ERROR_INVALID_PARAM,   /* Некоректний параметр */
    DRV8833_ERROR_NOT_INITIALIZED  /* Драйвер не ініціалізовано */
} drv8833_status_t;

/**
 * @brief Тип вказівника на функцію встановлення логічного рівня GPIO.
 * @param pin_id Номер/ідентифікатор виводу GPIO.
 * @param state Стан виводу (true = HIGH, false = LOW).
 */
typedef void (*drv8833_gpio_write_fn)(uint8_t pin_id, bool state);

/**
 * @brief Тип вказівника на функцію налаштування коефіцієнта заповнення ШІМ.
 * @param pwm_channel Номер/ідентифікатор каналу ШІМ.
 * @param duty_percent Коефіцієнт заповнення у відсотках (0..100).
 */
typedef void (*drv8833_pwm_set_duty_fn)(uint8_t pwm_channel, uint8_t duty_percent);

/**
 * @brief Апаратна конфігурація одного мотора.
 */
typedef struct {
    uint8_t pin_in1;     /* Вивід GPIO для входу 1 (IN1 або IN3) */
    uint8_t pin_in2;     /* Вивід GPIO для входу 2 (IN2 або IN4) */
    uint8_t pwm_ch_in1;  /* Канал ШІМ для входу 1 */
    uint8_t pwm_ch_in2;  /* Канал ШІМ для входу 2 */
} drv8833_motor_config_t;

/**
 * @brief Загальна конфігурація двоканального драйвера DRV8833.
 */
typedef struct {
    drv8833_motor_config_t motor_a;   /* Конфігурація мотора A */
    drv8833_motor_config_t motor_b;   /* Конфігурація мотора B */
    uint8_t pin_sleep;                /* Вивід nSLEEP (або DRV8833_PIN_UNUSED) */
    drv8833_gpio_write_fn gpio_write;  /* Апаратна функція запису GPIO */
    drv8833_pwm_set_duty_fn pwm_set;   /* Апаратна функція керування ШІМ */
} drv8833_config_t;

/**
 * @brief Поточний стан окремого мотора.
 */
typedef struct {
    drv8833_mode_t mode;    /* Поточний режим роботи */
    uint8_t speed_percent;  /* Поточна швидкість у відсотках (0..100) */
} drv8833_motor_state_t;

/**
 * @brief Структура дескриптора драйвера DRV8833.
 */
typedef struct {
    drv8833_config_t config;        /* Апаратна конфігурація */
    drv8833_motor_state_t state_a;  /* Стан мотора A */
    drv8833_motor_state_t state_b;  /* Стан мотора B */
    bool is_initialized;            /* Прапорець завершення ініціалізації */
    bool is_sleeping;               /* Прапорець активного режиму сну */
} drv8833_t;

/**
 * @brief Ініціалізація драйвера DRV8833 та первинне налаштування станів.
 * @param handle Дескриптор драйвера.
 * @param config Конфігурація периферії та функцій зворотного виклику.
 * @return DRV8833_OK або код помилки.
 */
drv8833_status_t drv8833_init(drv8833_t *handle, const drv8833_config_t *config);

/**
 * @brief Встановлення режиму руху та швидкості мотора.
 * @param handle Дескриптор драйвера.
 * @param motor Ідентифікатор мотора (A або B).
 * @param mode Режим (FORWARD, REVERSE, BRAKE, COAST).
 * @param speed_percent Швидкість обертання від 0 до 100%.
 * @return DRV8833_OK або код помилки.
 */
drv8833_status_t drv8833_set_motor(drv8833_t *handle, drv8833_motor_id_t motor, drv8833_mode_t mode, uint8_t speed_percent);

/**
 * @brief Зміна швидкості мотора без зміни поточної орієнтації руху.
 * @param handle Дескриптор драйвера.
 * @param motor Ідентифікатор мотора.
 * @param speed_percent Нова швидкість від 0 до 100%.
 * @return DRV8833_OK або код помилки.
 */
drv8833_status_t drv8833_set_speed(drv8833_t *handle, drv8833_motor_id_t motor, uint8_t speed_percent);

/**
 * @brief Активне електродинамічне гальмування мотора (коротке замикання обмотки).
 * @param handle Дескриптор драйвера.
 * @param motor Ідентифікатор мотора.
 * @return DRV8833_OK або код помилки.
 */
drv8833_status_t drv8833_brake(drv8833_t *handle, drv8833_motor_id_t motor);

/**
 * @brief Переведення виходів мотора у режим вільного вибігу (High-Z).
 * @param handle Дескриптор драйвера.
 * @param motor Ідентифікатор мотора.
 * @return DRV8833_OK або код помилки.
 */
drv8833_status_t drv8833_coast(drv8833_t *handle, drv8833_motor_id_t motor);

/**
 * @brief Переключення режиму енергозбереження nSLEEP.
 * @param handle Дескриптор драйвера.
 * @param sleep_enable true — увімкнути режим сну, false — вийти зі сну.
 * @return DRV8833_OK або код помилки.
 */
drv8833_status_t drv8833_set_sleep(drv8833_t *handle, bool sleep_enable);

/**
 * @brief Зчитування поточного стану мотора.
 * @param handle Дескриптор драйвера.
 * @param motor Ідентифікатор мотора.
 * @param state Вказівник на структуру для запису стану.
 * @return DRV8833_OK або код помилки.
 */
drv8833_status_t drv8833_get_motor_state(const drv8833_t *handle, drv8833_motor_id_t motor, drv8833_motor_state_t *state);

#endif /* DRV8833_H */
