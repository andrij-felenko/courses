#ifndef AHT20_H
#define AHT20_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file aht20.h
 * @brief Оголошення апаратно-незалежного драйвера цифрового давача температури та вологості AHT20.
 */

// I2C адреса давача AHT20 за замовчуванням (7-бітна)
#define AHT20_I2C_ADDR_DEFAULT        0x38

// Команди керування давачем AHT20
#define AHT20_CMD_INIT                0xBE
#define AHT20_CMD_TRIGGER             0xAC
#define AHT20_CMD_SOFT_RESET          0xBA

// Часові затримки в мілісекундах
#define AHT20_MEASURE_DELAY_MS        80
#define AHT20_POWER_ON_DELAY_MS       40
#define AHT20_SOFT_RESET_DELAY_MS     20

// Біти статусного байта AHT20
#define AHT20_STATUS_BUSY_BIT         0x80
#define AHT20_STATUS_CALIBRATED_BIT   0x08

/**
 * @brief Коди повернення та статуси помилок драйвера AHT20.
 */
typedef enum {
    AHT20_OK = 0,               // Операція успішна
    AHT20_BUSY,                 // Давач виконує вимірювання (не помилка, очікування)
    AHT20_ERR_I2C,              // Помилка обміну по шині I2C
    AHT20_ERR_NOT_CALIBRATED,   // Давач не відкалібрований
    AHT20_ERR_CRC,              // Помилка контрольної суми CRC-8
    AHT20_ERR_TIMEOUT,          // Перевищено час очікування готовності даних
    AHT20_ERR_INVALID_ARG       // Передано некоректні аргументи
} aht20_status_t;

/**
 * @brief Стан неблокуючого автомата станів драйвера AHT20.
 */
typedef enum {
    AHT20_STATE_IDLE = 0,       // Давач готовий до нового вимірювання
    AHT20_STATE_MEASURING       // Триває вимірювання (очікування 80 мс)
} aht20_state_t;

/**
 * @brief Структура для збереження отриманих фізичних величин.
 */
typedef struct {
    float temperature;          // Температура у градусах Цельсія (C)
    float humidity;             // Відносна вологість у відсотках (%)
} aht20_data_t;

/**
 * @brief Прототипи апаратно-залежних функцій зворотного виклику (HAL).
 */
typedef bool (*aht20_i2c_read_fn)(uint8_t dev_addr, uint8_t *data, size_t len, void *user_data);
typedef bool (*aht20_i2c_write_fn)(uint8_t dev_addr, const uint8_t *data, size_t len, void *user_data);
typedef uint32_t (*aht20_get_tick_ms_fn)(void);

/**
 * @brief Контекстна структура драйвера AHT20.
 */
typedef struct {
    uint8_t dev_addr;                  // I2C адреса давача
    aht20_i2c_read_fn i2c_read;        // Вказівник на функцію читання I2C
    aht20_i2c_write_fn i2c_write;      // Вказівник на функцію запису I2C
    aht20_get_tick_ms_fn get_tick;     // Вказівник на функцію системного часу (мс)
    void *user_data;                   // Користувацький контекст для I2C драйвера

    aht20_state_t state;               // Поточний стан автомата станів
    uint32_t start_tick;               // Позначка часу початку вимірювання
    bool is_calibrated;                // Прапорець успішного калібрування
} aht20_t;

/**
 * @brief Ініціалізація контексту драйвера AHT20 та перевірка калібрування.
 *
 * @param dev Вказівник на структуру контексту AHT20.
 * @param dev_addr 7-бітна I2C адреса пристрою (зазвичай 0x38).
 * @param read_fn Вказівник на апаратно-залежну функцію читання з I2C.
 * @param write_fn Вказівник на апаратно-залежну функцію запису в I2C.
 * @param tick_fn Вказівник на функцію отримання системного часу в мілісекундах.
 * @param user_data Вказівник на користувацький контекст (наприклад, дескриптор шини).
 * @return aht20_status_t Результат ініціалізації (AHT20_OK у разі успіху).
 */
aht20_status_t aht20_init(aht20_t *dev,
                          uint8_t dev_addr,
                          aht20_i2c_read_fn read_fn,
                          aht20_i2c_write_fn write_fn,
                          aht20_get_tick_ms_fn tick_fn,
                          void *user_data);

/**
 * @brief Програмне скидання давача AHT20 (команда 0xBA).
 *
 * @param dev Вказівник на контекст AHT20.
 * @return aht20_status_t Результат виконання.
 */
aht20_status_t aht20_reset(aht20_t *dev);

/**
 * @brief Запуск процесу вимірювання вологості та температури (неблокуючий).
 *
 * Пересилає команду 0xAC з параметрами 0x33 та 0x00, записує початковий час і переводить
 * автомат станів у стан AHT20_STATE_MEASURING.
 *
 * @param dev Вказівник на контекст AHT20.
 * @return aht20_status_t Результат запуску вимірювання.
 */
aht20_status_t aht20_start_measurement(aht20_t *dev);

/**
 * @brief Періодична функція оновлення автомата станів (неблокуюча).
 *
 * Перевіряє сплив часу 80 мс після запуску вимірювання. Якщо час сплив, зчитує 7-байтовий
 * пакет, перевіряє CRC-8 та перераховує фізичні значення.
 *
 * @param dev Вказівник на контекст AHT20.
 * @param data Вказівник на структуру для запису збережених результатів.
 * @return aht20_status_t AHT20_BUSY під час очікування, AHT20_OK при завершенні або код помилки.
 */
aht20_status_t aht20_update(aht20_t *dev, aht20_data_t *data);

/**
 * @brief Блокуюче зчитування даних із використанням затримки.
 *
 * Утилітарна функція для простих сценаріїв без неблокуючого автомата станів.
 *
 * @param dev Вказівник на контекст AHT20.
 * @param data Вказівник на структуру результатів.
 * @param delay_ms Вказівник на функцію системної затримки в мілісекундах.
 * @return aht20_status_t Результат зчитування.
 */
aht20_status_t aht20_read_blocking(aht20_t *dev, aht20_data_t *data, void (*delay_ms)(uint32_t));

/**
 * @brief Перевірка контрольної суми CRC-8 для пакета AHT20.
 *
 * Алгоритм CRC-8 (поліном 0x31, початкове значення 0xFF).
 *
 * @param data Вказівник на масив даних.
 * @param len Довжина масиву в байтах.
 * @return uint8_t Обчислене значення CRC-8.
 */
uint8_t aht20_calculate_crc8(const uint8_t *data, size_t len);

#endif // AHT20_H
