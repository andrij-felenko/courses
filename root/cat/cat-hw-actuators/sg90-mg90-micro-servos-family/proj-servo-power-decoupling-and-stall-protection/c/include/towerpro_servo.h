#ifndef TOWERPRO_SERVO_H
#define TOWERPRO_SERVO_H

#include <stdint.h>
#include <stdbool.h>
#include "pwm_driver.h"
#include "adc_current_sensor.h"

/**
 * @file towerpro_servo.h
 * @brief Модуль позиціонування та порогового струмового захисту для сервоприводів Tower Pro.
 *
 * Підтримує апаратні профілі для SG90, SG92R, MG90S та MG90D. Реалізує виявлення
 * заклинювання редуктора за RMS-струмом та автоматичне вимкнення ШІМ.
 */

/**
 * @brief Перелічення підтримуваних моделей сервоприводів родини Tower Pro
 */
typedef enum {
    SERVO_MODEL_SG90 = 0, /**< Пластиковий редуктор, пороговий струм ~500 мА */
    SERVO_MODEL_SG92R,    /**< Вуглеволоконний редуктор, пороговий струм ~600 мА */
    SERVO_MODEL_MG90S,    /**< Металевий редуктор, пороговий струм ~750 мА */
    SERVO_MODEL_MG90D     /**< Цифровий металевий редуктор, пороговий струм ~900 мА */
} servo_model_t;

/**
 * @brief Паспортний профіль характеристик моделі сервоприводу
 */
typedef struct {
    servo_model_t model;            /**< Модель сервоприводу */
    const char *model_name;         /**< Текстова назва моделі */
    uint16_t min_pulse_us;          /**< Тривалість імпульсу для кута 0° (мкс) */
    uint16_t max_pulse_us;          /**< Тривалість імпульсу для кута 180° (мкс) */
    float max_angle_deg;            /**< Максимальний робочий кут (градуси) */
    float stall_current_limit_ma;   /**< Поріг струму заклинювання (мА) */
    uint32_t stall_timeout_ms;      /**< Час утримання перевищення струму до спрацювання захисту (мс) */
} servo_profile_t;

/**
 * @brief Статус роботи сервоприводу
 */
typedef enum {
    SERVO_STATUS_OK = 0,            /**< Нормальна робота */
    SERVO_STATUS_BUSY,              /**< Позиціонування в процесі */
    SERVO_STATUS_STALLED,           /**< Аварійне заклинювання (ШІМ вимкнено) */
    SERVO_STATUS_ERROR              /**< Помилка ініціалізації або параметрів */
} servo_status_t;

/**
 * @brief Тип вказівника на користувацьку callback-функцію аварійного сповіщення
 */
typedef void (*servo_stall_callback_t)(void *user_data, servo_model_t model, float current_rms_ma);

/**
 * @brief Конструктор конфігурації сервоприводу
 */
typedef struct {
    servo_model_t model;            /**< Модель сервоприводу з серії Tower Pro */
    pwm_driver_t *pwm;              /**< Вказівник на ініціалізований ШІМ-драйвер */
    adc_sensor_t *adc;              /**< Вказівник на ініціалізований сенсор струму */
    servo_stall_callback_t stall_cb;/**< Аварійний обробник заклинювання */
    void *user_data;                /**< Довільний вказівник для користувацького контексту */
} servo_config_t;

/**
 * @brief Головна структура контексту сервоприводу
 */
typedef struct {
    servo_config_t config;          /**< Конфігураційні параметри */
    servo_profile_t profile;        /**< Завантажений профіль моделі */
    float target_angle_deg;         /**< Цільовий кут повороту (градуси) */
    float current_angle_deg;        /**< Поточний встановлений кут (градуси) */
    servo_status_t status;          /**< Поточний стан приводу */
    uint32_t stall_start_time_ms;   /**< Часова мітка початку перевищення струмового порогу */
    bool is_stalled;                /**< Прапорець зафіксованого заклинювання */
} towerpro_servo_t;

/**
 * @brief Повертає паспортний профіль конфігурації для вказаної моделі.
 * @param model Модель сервоприводу з перелічення servo_model_t
 * @return Структура servo_profile_t із попередньо налаштованими константами
 */
servo_profile_t towerpro_servo_get_profile(servo_model_t model);

/**
 * @brief Ініціалізує сервопривод, завантажує профіль та встановлює початковий кут 90°.
 * @param servo Вказівник на об'єкт сервоприводу
 * @param config Конфігураційні параметри
 * @return 0 при успіху, -1 при некоректних аргументах
 */
int towerpro_servo_init(towerpro_servo_t *servo, const servo_config_t *config);

/**
 * @brief Встановлює цільовий кут повороту вала.
 * @param servo Вказівник на об'єкт сервоприводу
 * @param angle_deg Заданий кут у градусах (0..180)
 * @return 0 при успіху, -1 у разі помилки або активного блокування через заклинювання
 */
int towerpro_servo_set_angle(towerpro_servo_t *servo, float angle_deg);

/**
 * @brief Неблокуюча функція обробки даних у фоновому циклі.
 * @param servo Вказівник на об'єкт сервоприводу
 * @param raw_adc_sample Нова вибірка АЦП струму
 * @param current_time_ms Поточний системний час у мілісекундах
 * @return 0 при нормальній роботі, -1 при аварійному відключенні ШІМ
 */
int towerpro_servo_process(towerpro_servo_t *servo, uint16_t raw_adc_sample, uint32_t current_time_ms);

/**
 * @brief Скидає стан заклинювання та відновлює подачу ШІМ-сигналу.
 * @param servo Вказівник на об'єкт сервоприводу
 * @return 0 при успіху, -1 при некоректному вказівнику
 */
int towerpro_servo_reset_fault(towerpro_servo_t *servo);

/**
 * @brief Повертає поточне значення RMS-струму споживання двигуна.
 * @param servo Вказівник на об'єкт сервоприводу
 * @return Струм у міліамперах
 */
float towerpro_servo_get_current_rms(const towerpro_servo_t *servo);

/**
 * @brief Повертає поточний статус системи сервоприводу.
 * @param servo Вказівник на об'єкт сервоприводу
 * @return Значення з перелічення servo_status_t
 */
servo_status_t towerpro_servo_get_status(const towerpro_servo_t *servo);

#endif /* TOWERPRO_SERVO_H */
