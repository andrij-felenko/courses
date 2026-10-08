/**
 * @file vl53l0x_array.h
 * @brief Оголошення драйвера масиву ToF-давачів VL53L0X для роботи на спільній шині I2C.
 *
 * Модуль забезпечує послідовне керування лініями скидання XSHUT для усунення конфліктів
 * однаково зашитих початкових I2C-адрес (0x29), динамічне перепризначення унікальних адрес,
 * конфігурацію SPAD-матриці, налаштування режиму безперервного вимірювання
 * (Continuous Ranging Mode) та неблокуюче асинхронне зчитання даних.
 */

#ifndef VL53L0X_ARRAY_H
#define VL53L0X_ARRAY_H

#include <stdint.h>
#include <stdbool.h>
#include "i2c_hal.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ========================================================================== */
/*                             КОНСТАНТИ ТА АДРЕСИ                            */
/* ========================================================================== */

#define VL53L0X_DEFAULT_I2C_ADDR    0x29U  /**< Фабрична 7-бітна I2C-адреса чипа після скидання */
#define VL53L0X_MAX_ARRAY_SIZE      4U     /**< Максимальна кількість давачів у масиві */
#define VL53L0X_EXPECTED_DEVICE_ID  0xEEU  /**< Очікуване значення регістра Model ID (0xC0) */

/* Регістри VL53L0X */
#define VL53L0X_REG_SYSRANGE_START                 0x00U  /**< Пуск вимірювання (0x01: single, 0x02: continuous) */
#define VL53L0X_REG_SYSTEM_SEQUENCE_CONFIG         0x01U  /**< Конфігурація послідовності вимірювання */
#define VL53L0X_REG_SYSTEM_INTERRUPT_CONFIG_GPIO   0x0AU  /**< Конфігурація режиму переривання INT (GPIO1) */
#define VL53L0X_REG_SYSTEM_INTERRUPT_CLEAR         0x0BU  /**< Скидання прапорця переривання (запис 0x01) */
#define VL53L0X_REG_RESULT_INTERRUPT_STATUS        0x13U  /**< Статус готовності переривання */
#define VL53L0X_REG_RESULT_RANGE_STATUS            0x14U  /**< Статус вимірювання та блок результатів (12 байт) */
#define VL53L0X_REG_RESULT_DISTANCE_MM             0x28U  /**< Адреса старшого байта (MSB) результату дистанції (мм) */
#define VL53L0X_REG_I2C_SLAVE_DEVICE_ADDRESS       0x8AU  /**< Регістр динамічного перепризначення I2C-адреси */
#define VL53L0X_REG_IDENTIFICATION_MODEL_ID        0xC0U  /**< Ідентифікатор моделі (0xEE) */

/* ========================================================================== */
/*                                ТИПИ ДАНИХ                                  */
/* ========================================================================== */

/**
 * @brief Перелічення статусів та помилок драйвера VL53L0X.
 */
typedef enum {
    VL53L0X_OK                  = 0,  /**< Операцію виконано успішно */
    VL53L0X_ERR_I2C             = 1,  /**< Апаратна помилка обміну по шині I2C */
    VL53L0X_ERR_WRONG_ID        = 2,  /**< Невірний ID чипа (відмінний від 0xEE) */
    VL53L0X_ERR_TIMEOUT         = 3,  /**< Перевищено час очікування готовності пристрою */
    VL53L0X_ERR_INVALID_PARAM   = 4,  /**< Передано некоректний аргумент */
    VL53L0X_ERR_CALIBRATION     = 5   /**< Збій ініціалізації SPAD-матриці чи опорного калібрування */
} vl53l0x_err_t;

/**
 * @brief Стан кінцевого автомата окремого пристрою VL53L0X.
 */
typedef enum {
    VL53L0X_STATE_SHUTDOWN      = 0,  /**< Лінія XSHUT в LOW (чип у стані апаратного скидання) */
    VL53L0X_STATE_BOOTING       = 1,  /**< Подано живлення, триває внутрішня завантаження чипа */
    VL53L0X_STATE_ADDRESS_ASSIGNED = 2,/**< Призначено нову унікальну I2C-адресу */
    VL53L0X_STATE_READY         = 3,  /**< Пройдено базову ініціалізацію, чип готовий */
    VL53L0X_STATE_RANGING       = 4,  /**< Чип у режимі безперервного генератора вимірювань */
    VL53L0X_STATE_ERROR         = 5   /**< Критичний апаратний збій сенсора */
} vl53l0x_state_t;

/**
 * @brief Структура контексту окремого ToF-давача.
 */
typedef struct {
    uint8_t id;                   /**< Індекс сенсора в масиві (0..N-1) */
    uint8_t current_addr;         /**< Поточна активна 7-бітна I2C-адреса */
    hal_gpio_pin_t xshut_pin;     /**< Апаратний вивід GPIO для ліній скидання XSHUT */
    hal_gpio_pin_t exti_pin;      /**< Апаратний вивід GPIO для переривання INT (GPIO1) */
    vl53l0x_state_t state;        /**< Поточний стан пристрою */
    uint16_t last_distance_mm;    /**< Останнє успішно виміряне значення дистанції (мм) */
    uint8_t range_status;         /**< Апаратний код якості вимірювання (0: Valid) */
    volatile bool data_ready_flag;/**< Прапорець готовності вимірювання (асинхронно від EXTI) */
    uint32_t read_count;          /**< Лічильник успішно зчитаних кадрів */
    uint32_t error_count;         /**< Лічильник помилок та пропускання кадрів */
} vl53l0x_dev_t;

/**
 * @brief Структура керування масивом ToF-давачів VL53L0X.
 */
typedef struct {
    vl53l0x_dev_t dev[VL53L0X_MAX_ARRAY_SIZE]; /**< Контексти всіх давачів масиву */
    uint8_t count;                             /**< Кількість активних давачів у масиві */
    bool is_initialized;                       /**< Прапорець успішного налаштування всієї системи */
} VL53L0X_Array_t;

/* ========================================================================== */
/*                             ПРОТОТИПИ ФУНКЦІЙ                              */
/* ========================================================================== */

/**
 * @brief Повний цикл послідовного виведення зі скидання, перепризначення адрес та ініціалізації масиву.
 * @param arr Вказівник на структуру масиву VL53L0X_Array_t.
 * @param target_addrs Масив нових 7-бітних I2C-адрес для кожного сенсора.
 * @param sensor_count Кількість сенсорів у масиві.
 * @return VL53L0X_OK у разі успішної ініціалізації всіх сенсорів.
 */
vl53l0x_err_t vl53l0x_array_init(VL53L0X_Array_t *arr, const uint8_t *target_addrs, uint8_t sensor_count);

/**
 * @brief Переведення всіх ліній XSHUT у низький рівень (апаратне скидання всіх чипів).
 * @param arr Вказівник на масив давачів.
 */
void vl53l0x_array_hardware_reset_all(VL53L0X_Array_t *arr);

/**
 * @brief Послідовна розконсервація XSHUT одного чипа та запис нової I2C-адреси.
 * @param dev Вказівник на контекст окремого давача.
 * @param new_i2c_addr Нова унікальна 7-бітна I2C-адреса.
 * @return VL53L0X_OK або відповідний код помилки.
 */
vl53l0x_err_t vl53l0x_sensor_poweron_and_readdress(vl53l0x_dev_t *dev, uint8_t new_i2c_addr);

/**
 * @brief Ініціалізація SPAD-матриці та завантаження базовго конфігураційного профілю VL53L0X.
 * @param dev Вказівник на контекст давача.
 * @return VL53L0X_OK або код помилки.
 */
vl53l0x_err_t vl53l0x_sensor_init_device(vl53l0x_dev_t *dev);

/**
 * @brief Запуск неблокуючого режиму безперервного вимірювання (Continuous Ranging Mode).
 * @param dev Вказівник на контекст давача.
 * @return VL53L0X_OK або код помилки.
 */
vl53l0x_err_t vl53l0x_start_continuous(vl53l0x_dev_t *dev);

/**
 * @brief Неблокуюче зчитування виміряної дистанції (мм) після отримання сигналу EXTI.
 * @param dev Вказівник на контекст давача.
 * @param p_distance_mm Вказівник для збереження значення відстані.
 * @return VL53L0X_OK якщо дистанцію успішно прочитано та підтверджено.
 */
vl53l0x_err_t vl53l0x_read_distance_async(vl53l0x_dev_t *dev, uint16_t *p_distance_mm);

/**
 * @brief Скидання апаратного прапорця переривання в регістрі пристрою.
 * @param dev Вказівник на контекст давача.
 * @return VL53L0X_OK або код помилки.
 */
vl53l0x_err_t vl53l0x_clear_interrupt(vl53l0x_dev_t *dev);

#ifdef __cplusplus
}
#endif

#endif /* VL53L0X_ARRAY_H */
