#ifndef DC_MOTOR_130_H
#define DC_MOTOR_130_H

#include <stdint.h>
#include <stdbool.h>
#include "mcu_pwm_gpio.h"

/**
 * @file dc_motor_130.h
 * @brief Оголошення модульного C-драйвера колекторного двигуна типорозміру 130.
 * 
 * Драйвер реалізує керування напрямком обертання вала (FORWARD / REVERSE),
 * регулювання швидкості через ШІМ, безпечне перемикання ключів H-моста
 * з програмною часовою паузою (Dead Time) та режими зупинки (COAST / BRAKE).
 */

/**
 * @brief Напрямок обертання вала колекторного двигуна.
 */
typedef enum {
    DC_MOTOR_DIR_STOP    = 0,  /**< Двигун знеструмлений / зупинений */
    DC_MOTOR_DIR_FORWARD = 1,  /**< Пряме обертання (Вперед) */
    DC_MOTOR_DIR_REVERSE = 2   /**< Зворотне обертання (Реверс / Назад) */
} dc_motor_direction_t;

/**
 * @brief Режими зупинки двигуна на рівні силового H-моста.
 */
typedef enum {
    DC_MOTOR_STOP_COAST = 0,  /**< Інерційний вибіг (High-Z): ключі H-моста розімкнені, вал обертається по інерції */
    DC_MOTOR_STOP_BRAKE = 1   /**< Активне гальмування: обмотки мотора коротко замкнені для поглинання проти-ЕРС */
} dc_motor_stop_mode_t;

/**
 * @brief Внутрішній стан роботи C-драйвера мотора.
 */
typedef enum {
    DC_MOTOR_STATE_IDLE      = 0,  /**< Простій / Двигун вимкнений */
    DC_MOTOR_STATE_RUNNING   = 1,  /**< Активне обертання вала */
    DC_MOTOR_STATE_DEAD_TIME = 2,  /**< Витримання часової паузи (Dead Time) перед зміною напрямку */
    DC_MOTOR_STATE_BRAKING   = 3   /**< Виконання активного реверсивного гальмування */
} dc_motor_state_t;

/**
 * @brief Статусні коди помилок драйвера колекторного двигуна.
 */
typedef enum {
    DC_MOTOR_OK              =  0,  /**< Успішне виконання операції */
    DC_MOTOR_ERR_NULL_PTR    = -1,  /**< Передано нульовий вказівник */
    DC_MOTOR_ERR_INVALID_DUTY= -2,  /**< Перевищено допустимий діапазон ШІМ (> 100%) */
    DC_MOTOR_ERR_INVALID_PARAM= -3, /**< Передано некоректний напрямок або режим зупинки */
    DC_MOTOR_ERR_NOT_INIT    = -4   /**< Драйвер мотора не було ініціалізовано */
} dc_motor_err_t;

/**
 * @brief Конфігураційна структура ініціалізації двигуна 130 типорозміру.
 */
typedef struct {
    uint8_t pin_in1;                   /**< Номер виводу GPIO MCU для керуючого сигналу IN1 */
    uint8_t pin_in2;                   /**< Номер виводу GPIO MCU для керуючого сигналу IN2 */
    uint8_t pwm_channel;               /**< Номер каналу ШІМ для виводу Enable (EN) */
    uint32_t pwm_frequency_hz;         /**< Частота ШІМ у Гц (рекомендовано 15–25 кГц для двигунів 130) */
    uint32_t dead_time_us;             /**< Тривалість захисної паузи Dead Time в мікросекундах */
    dc_motor_stop_mode_t default_stop; /**< Базовий режим зупинки за замовчуванням (COAST або BRAKE) */
} dc_motor_config_t;

/**
 * @brief Структура дескриптора (об'єкта) драйвера колекторного двигуна.
 */
typedef struct {
    dc_motor_config_t config;          /**< Збережена конфігурація периферії та таймінгу */
    dc_motor_direction_t direction;    /**< Поточний напрямок обертання (STOP, FORWARD, REVERSE) */
    dc_motor_stop_mode_t stop_mode;    /**< Активний режим зупинки */
    dc_motor_state_t state;            /**< Поточний внутрішній стан мотора */
    uint8_t duty_cycle;                /**< Поточний коефіцієнт заповнення ШІМ у відсотках (0..100%) */
    bool is_initialized;               /**< Прапорець успішної ініціалізації драйвера */
} dc_motor_t;

/* --- Прототипи функцій API C-драйвера --- */

/**
 * @brief Ініціалізація C-драйвера колекторного двигуна та низькорівневої периферії MCU.
 * 
 * @param motor Вказівник на екземпляр дескриптора двигуна.
 * @param config Вказівник на структуру конфігурації.
 * @return DC_MOTOR_OK при успішній конфігурації GPIO та ШІМ.
 */
dc_motor_err_t dc_motor_init(dc_motor_t *motor, const dc_motor_config_t *config);

/**
 * @brief Динамічне встановлення коефіцієнта заповнення ШІМ (швидкості обертання).
 * 
 * @param motor Вказівник на дескриптор двигуна.
 * @param duty_percent Коефіцієнт заповнення у відсотках (0..100%).
 * @return DC_MOTOR_OK при успішному оновленні регістра ШІМ.
 */
dc_motor_err_t dc_motor_set_speed(dc_motor_t *motor, uint8_t duty_percent);

/**
 * @brief Безпечна зміна напрямку обертання двигуна із витриманням Dead Time.
 * 
 * При зміні напрямку обертання з FORWARD на REVERSE (чи навпаки) функція
 * примусово вимикає ключі H-моста на час dead_time_us для запобігання
 * наскрізним струмам короткого замикання.
 * 
 * @param motor Вказівник на дескриптор двигуна.
 * @param dir Новий напрямок (DC_MOTOR_DIR_FORWARD або DC_MOTOR_DIR_REVERSE).
 * @return DC_MOTOR_OK при успішній зміні напрямку.
 */
dc_motor_err_t dc_motor_set_direction(dc_motor_t *motor, dc_motor_direction_t dir);

/**
 * @brief Комплексний запуск двигуна із вказуванням напрямку та швидкості.
 * 
 * @param motor Вказівник на дескриптор двигуна.
 * @param dir Напрямок обертання.
 * @param duty_percent Швидкість обертання у відсотках (0..100%).
 * @return DC_MOTOR_OK при успішній виконанні.
 */
dc_motor_err_t dc_motor_drive(dc_motor_t *motor, dc_motor_direction_t dir, uint8_t duty_percent);

/**
 * @brief Коректна зупинка двигуна у вибраному режимі (вибіг або активне гальмування).
 * 
 * @param motor Вказівник на дескриптор двигуна.
 * @param mode Режим зупинки (DC_MOTOR_STOP_COAST або DC_MOTOR_STOP_BRAKE).
 * @return DC_MOTOR_OK у разі успішної зупинки.
 */
dc_motor_err_t dc_motor_stop(dc_motor_t *motor, dc_motor_stop_mode_t mode);

/**
 * @brief Аварійна негайна зупинка двигуна з відключенням ШІМ та ключів.
 * 
 * @param motor Вказівник на дескриптор двигуна.
 * @return DC_MOTOR_OK у разі успіху.
 */
dc_motor_err_t dc_motor_emergency_stop(dc_motor_t *motor);

/**
 * @brief Отримання текстового опису коду помилки.
 * @param err Код помилки.
 * @return Рядок з описом помилки українською мовою.
 */
const char* dc_motor_err_to_string(dc_motor_err_t err);

/**
 * @brief Отримання текстового опису напрямку обертання.
 * @param dir Напрямок обертання.
 * @return Назва напрямку українською мовою.
 */
const char* dc_motor_dir_to_string(dc_motor_direction_t dir);

/**
 * @brief Отримання текстового опису режиму зупинки.
 * @param mode Режим зупинки.
 * @return Назва режиму українською мовою.
 */
const char* dc_motor_stop_mode_to_string(dc_motor_stop_mode_t mode);

#endif /* DC_MOTOR_130_H */
