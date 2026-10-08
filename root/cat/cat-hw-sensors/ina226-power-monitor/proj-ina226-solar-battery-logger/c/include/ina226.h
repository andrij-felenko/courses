#ifndef INA226_H
#define INA226_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file ina226.h
 * @brief Оголошення низькорівневого C-драйвера для цифрового монітора живлення INA226.
 *
 * Драйвер підтримує конфігурування регістрів пристрою через шину I2C,
 * розрахунок та запис регістра калібрування, обробку 16-бітних двобайтових
 * знакових (доповняльний код) та беззнакових регістрів у форматі Big-Endian,
 * а також перетворення сирих даних у фізичні величини (В, А, Вт).
 */

/* --- Базова адреса I2C та ідентифікатори пристрою --- */
#define INA226_I2C_ADDR_DEFAULT       0x40  /**< Базова I2C адреса за замовчуванням (A0=GND, A1=GND) */
#define INA226_MANUFACTURER_ID_VAL    0x5449/**< Ідентифікатор виробника Texas Instruments ("TI") */
#define INA226_DIE_ID_VAL             0x2260/**< Ідентифікатор кристала INA226 */

/* --- Регістри INA226 --- */
#define INA226_REG_CONFIG             0x00  /**< Конфігураційний регістр */
#define INA226_REG_SHUNT_VOLTAGE      0x01  /**< Напруга на шунті (знаковий, 2.5 мкВ/LSB) */
#define INA226_REG_BUS_VOLTAGE        0x02  /**< Напруга на шині живлення (беззнаковий, 1.25 мВ/LSB) */
#define INA226_REG_POWER              0x03  /**< Потужність (беззнаковий, Power_LSB = 25 * Current_LSB) */
#define INA226_REG_CURRENT            0x04  /**< Струм (знаковий, Current_LSB) */
#define INA226_REG_CALIBRATION        0x05  /**< Регістр калібрування */
#define INA226_REG_MASK_ENABLE        0x06  /**< Регістр маски/увімкнення переривань Alert */
#define INA226_REG_ALERT_LIMIT        0x07  /**< Регістр порогового значення Alert */
#define INA226_REG_MANUFACTURER_ID    0xFE  /**< Регістр ID виробника */
#define INA226_REG_DIE_ID             0xFF  /**< Регістр ID мікросхеми */

/* --- Біти та маски конфігурації --- */
#define INA226_CONFIG_RESET           (1U << 15) /**< Біт програмного скиду (Software Reset) */

/**
 * @brief Режими усереднення вибірок (Averaging Mode - AVG[2:0]).
 */
typedef enum {
    INA226_AVG_1    = 0x00, /**< 1 вибірка (без усереднення) */
    INA226_AVG_4    = 0x01, /**< Усереднення по 4 вибірках */
    INA226_AVG_16   = 0x02, /**< Усереднення по 16 вибірках */
    INA226_AVG_64   = 0x03, /**< Усереднення по 64 вибірках */
    INA226_AVG_128  = 0x04, /**< Усереднення по 128 вибірках */
    INA226_AVG_256  = 0x05, /**< Усереднення по 256 вибірках */
    INA226_AVG_512  = 0x06, /**< Усереднення по 512 вибірках */
    INA226_AVG_1024 = 0x07  /**< Усереднення по 1024 вибірках */
} ina226_averaging_t;

/**
 * @brief Час перетворення ADC для напруги шини або шунта (Conversion Time - CT[2:0]).
 */
typedef enum {
    INA226_CONV_TIME_140US  = 0x00, /**< 140 мікросекунд */
    INA226_CONV_TIME_204US  = 0x01, /**< 204 мікросекунди */
    INA226_CONV_TIME_332US  = 0x02, /**< 332 мікросекунди */
    INA226_CONV_TIME_588US  = 0x03, /**< 588 мікросекунд */
    INA226_CONV_TIME_1100US = 0x04, /**< 1.1 мілісекунда (за замовчуванням) */
    INA226_CONV_TIME_2116US = 0x05, /**< 2.116 мілісекунди */
    INA226_CONV_TIME_4156US = 0x06, /**< 4.156 мілісекунди */
    INA226_CONV_TIME_8244US = 0x07  /**< 8.244 мілісекунди */
} ina226_conv_time_t;

/**
 * @brief Режими роботи ADC (Operating Mode - MODE[2:0]).
 */
typedef enum {
    INA226_MODE_POWER_DOWN        = 0x00, /**< Вимкнено / Сплячий режим */
    INA226_MODE_SHUNT_TRIGGERED   = 0x01, /**< Напруга шунта, по команді (Triggered) */
    INA226_MODE_BUS_TRIGGERED     = 0x02, /**< Напруга шини, по команді (Triggered) */
    INA226_MODE_SHUNT_BUS_TRIG    = 0x03, /**< Напруга шунта та шини, по команді */
    INA226_MODE_ADC_OFF           = 0x04, /**< АЦП вимкнено */
    INA226_MODE_SHUNT_CONTINUOUS  = 0x05, /**< Напруга шунта, безперервно */
    INA226_MODE_BUS_CONTINUOUS    = 0x06, /**< Напруга шини, безперервно */
    INA226_MODE_SHUNT_BUS_CONT    = 0x07  /**< Напруга шунта та шини, безперервно (за замовчуванням) */
} ina226_mode_t;

/**
 * @brief Коди результатів та помилок драйвера INA226.
 */
typedef enum {
    INA226_OK                  =  0, /**< Операцію виконано успішно */
    INA226_ERR_INVALID_PARAM   = -1, /**< Передано некоректні аргументи */
    INA226_ERR_I2C             = -2, /**< Помилка обміну по шині I2C */
    INA226_ERR_DEV_NOT_FOUND   = -3, /**< Пристрій не відповідає або ID не збігається */
    INA226_ERR_CALIBRATION     = -4  /**< Помилка розрахунку регістра калібрування */
} ina226_err_t;

/**
 * @brief Прототипи функцій запису/читання по шині I2C (HAL абстракція).
 */
typedef ina226_err_t (*ina226_i2c_write_fn)(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, uint16_t len);
typedef ina226_err_t (*ina226_i2c_read_fn)(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, uint16_t len);

/**
 * @brief Структура первинних налаштувань INA226.
 */
typedef struct {
    uint8_t i2c_addr;             /**< I2C адреса пристрою (0x40..0x4F) */
    float r_shunt_ohms;           /**< Опір вимірювального шунта в Омах (наприклад, 0.01 Ом) */
    float max_expected_current_a; /**< Максимальний очікуваний струм в Амперах */
    ina226_averaging_t avg_mode;  /**< Кількість усереднень АЦП */
    ina226_conv_time_t vbus_ct;   /**< Час вимірювання напруги шини */
    ina226_conv_time_t vsh_ct;    /**< Час вимірювання напруги шунта */
    ina226_mode_t mode;           /**< Режим вимірювання АЦП */
    ina226_i2c_write_fn i2c_write;/**< Указівник на функцію запису I2C */
    ina226_i2c_read_fn i2c_read;  /**< Указівник на функцію читання I2C */
} ina226_config_t;

/**
 * @brief Контекст драйвера INA226.
 */
typedef struct {
    ina226_config_t config;       /**< Скопійовані налаштування пристрою */
    float current_lsb_a;          /**< Значення 1 LSB струму в Амперах */
    float power_lsb_w;            /**< Значення 1 LSB потужності у Ватах */
    uint16_t cal_value;           /**< Значення калібрувального регістра CAL */
    bool is_initialized;          /**< Прапорець успішної ініціалізації драйвера */
} ina226_handle_t;

/**
 * @brief Структура виміряних фізичних та сирих параметрів живлення.
 */
typedef struct {
    float shunt_voltage_v;  /**< Падіння напруги на шунті (В) */
    float bus_voltage_v;    /**< Напруга шини живлення (В) */
    float current_a;        /**< Виміряний струм навантаження (А) */
    float power_w;          /**< Обчислена миттєва потужність (Вт) */
    int16_t raw_shunt_reg;  /**< Сировий знаковий двобайтовий регістр шунта */
    uint16_t raw_bus_reg;   /**< Сировий беззнаковий двобайтовий регістр шини */
    int16_t raw_current_reg;/**< Сировий знаковий двобайтовий регістр струму */
    uint16_t raw_power_reg; /**< Сировий беззнаковий двобайтовий регістр потужності */
} ina226_data_t;

/* --- Прототипи функцій драйвера INA226 --- */

/**
 * @brief Ініціалізація давача INA226, конфігурування АЦП та запис калібрування.
 * @param handle Указівник на контекст драйвера.
 * @param config Указівник на структуру налаштувань.
 * @return INA226_OK у разі успіху або код помилки INA226.
 */
ina226_err_t ina226_init(ina226_handle_t *handle, const ina226_config_t *config);

/**
 * @brief Програмний скид (Soft Reset) мікросхеми INA226.
 * @param handle Указівник на контекст драйвера.
 * @return INA226_OK у разі успіху.
 */
ina226_err_t ina226_soft_reset(ina226_handle_t *handle);

/**
 * @brief Обчислення та запис регістра калібрування (Calibration Register).
 * @param handle Указівник на контекст драйвера.
 * @param r_shunt_ohms Опір шунта в Омах.
 * @param max_expected_current_a Максимальний струм у Амперах.
 * @return INA226_OK у разі успіху.
 */
ina226_err_t ina226_calibrate(ina226_handle_t *handle, float r_shunt_ohms, float max_expected_current_a);

/**
 * @brief Зчитати 16-бітний регістр INA226 з перетворенням з Big-Endian.
 * @param handle Указівник на контекст драйвера.
 * @param reg_addr Адреса регістра.
 * @param value Указівник для збереження прочитаного значення.
 * @return INA226_OK у разі успіху.
 */
ina226_err_t ina226_read_reg_16(ina226_handle_t *handle, uint8_t reg_addr, uint16_t *value);

/**
 * @brief Записати 16-бітне значення у регістр INA226 у форматі Big-Endian.
 * @param handle Указівник на контекст драйвера.
 * @param reg_addr Адреса регістра.
 * @param value Значення для запису.
 * @return INA226_OK у разі успіху.
 */
ina226_err_t ina226_write_reg_16(ina226_handle_t *handle, uint8_t reg_addr, uint16_t value);

/**
 * @brief Зчитування всіх виміряних величин (напруга шунта, напруга шини, струм, потужність).
 * @param handle Указівник на контекст драйвера.
 * @param data Указівник на структуру для збереження результатів.
 * @return INA226_OK у разі успіху.
 */
ina226_err_t ina226_read_data(ina226_handle_t *handle, ina226_data_t *data);

/**
 * @brief Зчитати лише напругу на вимірювальному шунті (Вольти).
 * @param handle Указівник на контекст драйвера.
 * @param shunt_v Указівник на змінну напруги шунта.
 * @return INA226_OK у разі успіху.
 */
ina226_err_t ina226_read_shunt_voltage(ina226_handle_t *handle, float *shunt_v);

/**
 * @brief Зчитати лише напругу шини живлення (Вольти).
 * @param handle Указівник на контекст драйвера.
 * @param bus_v Указівник на змінну напруги шини.
 * @return INA226_OK у разі успіху.
 */
ina226_err_t ina226_read_bus_voltage(ina226_handle_t *handle, float *bus_v);

/**
 * @brief Зчитати лише струм навантаження (Ампери).
 * @param handle Указівник на контекст драйвера.
 * @param current_a Указівник на змінну струму.
 * @return INA226_OK у разі успіху.
 */
ina226_err_t ina226_read_current(ina226_handle_t *handle, float *current_a);

/**
 * @brief Зчитати лише миттєву потужність (Вати).
 * @param handle Указівник на контекст драйвера.
 * @param power_w Указівник на змінну потужності.
 * @return INA226_OK у разі успіху.
 */
ina226_err_t ina226_read_power(ina226_handle_t *handle, float *power_w);

#endif /* INA226_H */
