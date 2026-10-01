#ifndef INA226_H
#define INA226_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Базова 7-бітна I2C-адреса INA226 за замовчуванням (A0=GND, A1=GND)
#define INA226_I2C_ADDR_DEFAULT      0x40

// Адреси регістрів INA226 (16-бітні регістри, порядок байтів Big-Endian)
#define INA226_REG_CONFIG            0x00 // Конфігурація (R/W)
#define INA226_REG_SHUNTVOLT         0x01 // Напруга на шунті (R)
#define INA226_REG_BUSVOLT           0x02 // Напруга шини живлення (R)
#define INA226_REG_POWER             0x03 // Потужність (R)
#define INA226_REG_CURRENT           0x04 // Струм (R)
#define INA226_REG_CALIBRATION       0x05 // Калібрування (R/W)
#define INA226_REG_MASK_ENABLE       0x06 // Маска переривань ALERT / Прапори (R/W)
#define INA226_REG_ALERT_LIMIT       0x07 // Поріг спрацьовування ALERT (R/W)
#define INA226_REG_MANUFACTURER_ID   0xFE // ID виробника (0x5449 = "TI")
#define INA226_REG_DIE_ID            0xFF // ID кристала (0x2260)

// Константні ідентифікатори Texas Instruments
#define INA226_MANUFACTURER_ID_VAL   0x5449
#define INA226_DIE_ID_VAL            0x2260

// Біт апаратного скидання у регістрі Конфігурації
#define INA226_CONFIG_RESET          (1U << 15)

// Режими усереднення вибірок (AVG, біти 11-9)
#define INA226_AVG_1                 (0x0U << 9)
#define INA226_AVG_4                 (0x1U << 9)
#define INA226_AVG_16                (0x2U << 9)
#define INA226_AVG_64                (0x3U << 9)
#define INA226_AVG_128               (0x4U << 9)
#define INA226_AVG_256               (0x5U << 9)
#define INA226_AVG_512               (0x6U << 9)
#define INA226_AVG_1024              (0x7U << 9)

// Час перетворення АЦП для напруги шини (VBUS CT, біти 8-6)
#define INA226_VBUS_140US            (0x0U << 6)
#define INA226_VBUS_204US            (0x1U << 6)
#define INA226_VBUS_332US            (0x2U << 6)
#define INA226_VBUS_588US            (0x3U << 6)
#define INA226_VBUS_1100US           (0x4U << 6)
#define INA226_VBUS_2116US           (0x5U << 6)
#define INA226_VBUS_4156US           (0x6U << 6)
#define INA226_VBUS_8244US           (0x7U << 6)

// Час перетворення АЦП для напруги шунта (VSH CT, біти 5-3)
#define INA226_VSH_140US             (0x0U << 3)
#define INA226_VSH_204US             (0x1U << 3)
#define INA226_VSH_332US             (0x2U << 3)
#define INA226_VSH_588US             (0x3U << 3)
#define INA226_VSH_1100US            (0x4U << 3)
#define INA226_VSH_2116US            (0x5U << 3)
#define INA226_VSH_4156US            (0x6U << 3)
#define INA226_VSH_8244US            (0x7U << 3)

// Режими роботи АЦП (MODE, біти 2-0)
#define INA226_MODE_POWER_DOWN       0x0U
#define INA226_MODE_SHUNT_TRIG       0x1U
#define INA226_MODE_BUS_TRIG         0x2U
#define INA226_MODE_SHUNT_BUS_TRIG   0x3U
#define INA226_MODE_ADC_OFF          0x4U
#define INA226_MODE_SHUNT_CONT       0x5U
#define INA226_MODE_BUS_CONT         0x6U
#define INA226_MODE_SHUNT_BUS_CONT   0x7U

// Біти конфігурації маски та прапорів статусів у регістрі MASK/ENABLE (0x06)
#define INA226_MASK_SOL              (1U << 15) // Over-Voltage на шунті
#define INA226_MASK_SUL              (1U << 14) // Under-Voltage на шунті
#define INA226_MASK_BOL              (1U << 13) // Over-Voltage на шині
#define INA226_MASK_BUL              (1U << 12) // Under-Voltage на шині
#define INA226_MASK_POL              (1U << 11) // Power Over-Limit (перевищення потужності)
#define INA226_MASK_CNVR             (1U << 10) // Переривання готовності вимірювання (Conversion Ready)
#define INA226_FLAG_AFF              (1U << 4)  // Прапор спрацьовування порогу ALERT (Alert Function Flag)
#define INA226_FLAG_CVRF             (1U << 3)  // Прапор завершення перетворення (Conversion Ready Flag)
#define INA226_FLAG_OVF              (1U << 2)  // Прапор математичного переповнення (Math Overflow Flag)
#define INA226_MASK_APOL             (1U << 1)  // Полярність виходу ALERT: 1 = Active High, 0 = Active Low
#define INA226_MASK_LEN              (1U << 0)  // Режим фіксації: 1 = Latched, 0 = Transparent

// Типи функцій зчитування та запису I2C для апаратної незалежності (HAL)
typedef bool (*ina226_i2c_write_fn)(uint8_t dev_addr, const uint8_t *data, size_t len);
typedef bool (*ina226_i2c_read_fn)(uint8_t dev_addr, uint8_t *data, size_t len);

// Конфігураційна структура INA226
typedef struct {
    uint8_t  i2c_addr;        // 7-бітна I2C адреса пристрою
    uint32_t r_shunt_mohm;   // Опір токовимірювального шунта в міліомах (мОм)
    uint32_t current_lsb_ua; // Роздільна здатність струму (Current LSB) у мікроамперах (мкА/LSB)
    uint16_t avg_samples;    // Кількість усреднюваних вибірок (наприклад INA226_AVG_16)
    uint16_t vbus_ct;        // Час перетворення напруги шини (наприклад INA226_VBUS_1100US)
    uint16_t vsh_ct;         // Час перетворення напруги шунта (наприклад INA226_VSH_1100US)
    uint16_t mode;           // Режим роботи АЦП (наприклад INA226_MODE_SHUNT_BUS_CONT)
} ina226_config_t;

// Структура виміряних фізичних величин (без рухомої коми)
typedef struct {
    uint32_t bus_voltage_mv;   // Напруга шини в мілівольтах (мВ)
    int32_t  shunt_voltage_uv; // Напруга шунта в мікровольтах (мкВ)
    int32_t  current_ma;       // Струм у міліамперах (мА)
    uint32_t power_mw;         // Потужність у міліватах (мВт)
} ina226_data_t;

// Дескриптор драйвера INA226
typedef struct {
    ina226_config_t     config;
    uint16_t            cal_value;
    ina226_i2c_write_fn i2c_write;
    ina226_i2c_read_fn  i2c_read;
} ina226_t;

// Прототипи функцій драйвера
bool ina226_init(ina226_t *dev, const ina226_config_t *cfg, ina226_i2c_write_fn w_fn, ina226_i2c_read_fn r_fn);
bool ina226_reset(ina226_t *dev);
bool ina226_check_id(ina226_t *dev);
uint16_t ina226_calc_calibration(uint32_t r_shunt_mohm, uint32_t current_lsb_ua);
bool ina226_write_calibration(ina226_t *dev);
bool ina226_read_bus_voltage(ina226_t *dev, uint32_t *voltage_mv);
bool ina226_read_shunt_voltage(ina226_t *dev, int32_t *voltage_uv);
bool ina226_read_current(ina226_t *dev, int32_t *current_ma);
bool ina226_read_power(ina226_t *dev, uint32_t *power_mw);
bool ina226_read_all(ina226_t *dev, ina226_data_t *data);
bool ina226_configure_alert(ina226_t *dev, uint16_t mask_flags, uint16_t limit_raw);
bool ina226_read_mask_enable(ina226_t *dev, uint16_t *flags);

#endif // INA226_H
