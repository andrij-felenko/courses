#ifndef AHT20_BMP280_H
#define AHT20_BMP280_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file aht20_bmp280.h
 * @brief Заголовний файл неблокувального драйвера комбінованого метеовузла AHT20 + BMP280.
 *
 * Модуль реалізує одночасне асинхронне опитування сенсорів температури,
 * вологості та тиску на спільній шині I2C із застосуванням скінченного
 * автомата (FSM), CRC-8 валідації та медіанної фільтрації.
 */

/* 7-бітні адреси пристроїв на шині I2C */
#define AHT20_I2C_ADDR       0x38
#define BMP280_I2C_ADDR      0x76

/* Розмір вікна медіанної фільтрації для придушення імпульсних завад */
#define MEDIAN_WINDOW_SIZE   5

/**
 * @brief Структура для зберігання заводських калібрувальних коефіцієнтів BMP280.
 */
typedef struct {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
    uint16_t dig_P1;
    int16_t  dig_P2;
    int16_t  dig_P3;
    int16_t  dig_P4;
    int16_t  dig_P5;
    int16_t  dig_P6;
    int16_t  dig_P7;
    int16_t  dig_P8;
    int16_t  dig_P9;
} bmp280_calib_param_t;

/**
 * @brief Структура кільцевого буфера медіанного фільтра.
 */
typedef struct {
    float buffer[MEDIAN_WINDOW_SIZE];
    uint8_t count;
    uint8_t index;
} median_filter_t;

/**
 * @brief Зведена структура фінальних кліматичних показників.
 */
typedef struct {
    float temperature_c;     /**< Обчислена та відфільтрована температура (°C) */
    float humidity_percent;  /**< Обчислена та відфільтрована вологість (%) */
    float pressure_hpa;      /**< Обчислений та відфільтрований тиск (гПа) */
    bool valid;              /**< Прапорець цілісності та достовірності відліку */
    uint32_t timestamp_ms;   /**< Часова позначка вимірювання (мс) */
} climate_data_t;

/**
 * @brief Стани неблокувального скінченного автомата (FSM).
 */
typedef enum {
    SENSOR_FSM_IDLE = 0,      /**< Очікування чергового інтервалу вимірювання */
    SENSOR_FSM_START_MEASURE, /**< Надсилання асинхронних команд запуску вимірів */
    SENSOR_FSM_WAIT_MEASURE,  /**< Неблокувальне очікування готовності датчиків */
    SENSOR_FSM_READ_DATA,     /**< Зчитування сирих байтів через I2C */
    SENSOR_FSM_PROCESS_DATA,  /**< Валідація CRC-8, компенсаційні розрахунки та фільтрація */
    SENSOR_FSM_ERROR          /**< Обробка помилок шини або датчиків */
} sensor_fsm_state_t;

/**
 * @brief Коди результатів виконання функцій драйвера.
 */
typedef enum {
    SENSOR_OK = 0,
    SENSOR_BUSY,
    SENSOR_ERR_I2C,
    SENSOR_ERR_CRC,
    SENSOR_ERR_CALIB,
    SENSOR_ERR_PARAM
} sensor_status_t;

/**
 * @brief Сигнатури адаптерів читання/запису I2C для прив'язки до платформи (HAL).
 */
typedef sensor_status_t (*i2c_read_fn)(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, size_t len);
typedef sensor_status_t (*i2c_write_fn)(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, size_t len);

/**
 * @brief Контекстний об'єкт драйвера кліматичного вузла.
 */
typedef struct {
    i2c_read_fn i2c_read;             /**< Вказівник на функцію читання I2C */
    i2c_write_fn i2c_write;           /**< Вказівник на функцію запису I2C */

    bmp280_calib_param_t bmp280_calib;/**< Калібрувальні дані BMP280 */
    int32_t bmp280_t_fine;            /**< Проміжне значення для компенсації тиску BMP280 */

    sensor_fsm_state_t state;         /**< Поточний стан FSM */
    uint32_t poll_interval_ms;        /**< Заданий інтервал опитування (мс) */
    uint32_t last_poll_ms;            /**< Час останнього вимірювання (мс) */
    uint32_t measure_start_ms;        /**< Час старту вимірювання (мс) */

    median_filter_t temp_filter;      /**< Фільтр температури */
    median_filter_t hum_filter;       /**< Фільтр вологості */
    median_filter_t press_filter;     /**< Фільтр тиску */

    climate_data_t climate_data;      /**< Останні розраховані кліматичні дані */
    bool is_initialized;              /**< Прапорець успішної ініціалізації */
    bool new_data_available;          /**< Прапорець наявності нового відліку */
} sensor_driver_t;

/* --- Прототипи функцій публічного API --- */

/**
 * @brief Ініціалізація драйвера, перевірка зв'язку та зчитування калібрувань BMP280.
 * @param driver Вказівник на структуру контексту.
 * @param read_fn Функція читання I2C.
 * @param write_fn Функція запису I2C.
 * @param poll_interval_ms Інтервал між оновленнями у мілісекундах.
 * @return SENSOR_OK у разі успіху.
 */
sensor_status_t sensor_driver_init(sensor_driver_t *driver,
                                   i2c_read_fn read_fn,
                                   i2c_write_fn write_fn,
                                   uint32_t poll_interval_ms);

/**
 * @brief Головний виклик оновлення FSM драйвера (неблокувальний).
 * @param driver Вказівник на структуру контексту.
 * @param current_time_ms Поточний системний час у мілісекундах.
 * @return Поточний статус обробки.
 */
sensor_status_t sensor_driver_update_fsm(sensor_driver_t *driver, uint32_t current_time_ms);

/**
 * @brief Зчитування поточних кліматичних даних.
 * @param driver Вказівник на структуру контексту.
 * @param out_data Вказівник на структуру для збереження результату.
 * @return true, якщо збережені дані актуальні та не зчитувалися раніше.
 */
bool sensor_driver_get_climate(sensor_driver_t *driver, climate_data_t *out_data);

/**
 * @brief Ініціалізація структури медіанного фільтра.
 * @param filter Вказівник на об'єкт фільтра.
 */
void median_filter_init(median_filter_t *filter);

/**
 * @brief Додавання нового значення у медіанний фільтр та отримання відфільтрованого результату.
 * @param filter Вказівник на об'єкт фільтра.
 * @param sample Нове виміряне значення.
 * @return Медіанне значення з поточного вікна.
 */
float median_filter_update(median_filter_t *filter, float sample);

#endif /* AHT20_BMP280_H */
