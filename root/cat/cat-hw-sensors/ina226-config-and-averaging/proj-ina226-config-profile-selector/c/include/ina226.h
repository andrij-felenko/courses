/**
 * @file ina226.h
 * @brief Заголовочний файл C-драйвера та кінцевого автомата (FSM) давача INA226.
 *
 * Визначення регістрів, бітових масок, режимів усереднення (AVG), часу перетворення
 * (VSHCT/VBUSCT), конфігураційних профілів та програмного інтерфейсу для STM32.
 */

#ifndef INA226_H
#define INA226_H

#include <stdint.h>
#include <stdbool.h>
#include "i2c_driver.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ========================================================================== */
/*                          АДРЕСИ РЕГІСТРІВ INA226                           */
/* ========================================================================== */

#define INA226_REG_CONFIG           0x00U  /**< Конфігурація (AVG, CT, MODE, RST) */
#define INA226_REG_SHUNTVOLT        0x01U  /**< Падіння напруги на шунті (int16, LSB = 2.5 мкВ) */
#define INA226_REG_BUSVOLT          0x02U  /**< Напруга силової шини (uint16, LSB = 1.25 мВ) */
#define INA226_REG_POWER            0x03U  /**< Обчислена потужність (uint16, LSB = 25 * Current_LSB) */
#define INA226_REG_CURRENT          0x04U  /**< Обчислений струм (int16, LSB = Current_LSB) */
#define INA226_REG_CALIBRATION      0x05U  /**< Калібрувальний коефіцієнт */
#define INA226_REG_MASK_ENABLE      0x06U  /**< Маска переривань та прапорець CVRF */
#define INA226_REG_ALERT_LIMIT      0x07U  /**< Поріг спрацювання сигналу ALERT */
#define INA226_REG_MANUFACTURER_ID  0xFEU  /**< ID виробника Texas Instruments (0x5449) */
#define INA226_REG_DIE_ID          0xFFU  /**< ID кристала чипа (0x2260) */

#define INA226_MANUFACTURER_ID_VAL  0x5449U
#define INA226_DIE_ID_VAL           0x2260U

/* ========================================================================== */
/*                  БІТОВІ МАСКИ РЕГІСТРА CONFIGURATION (0x00)                 */
/* ========================================================================== */

#define INA226_CONFIG_RST_MASK      (1U << 15)  /**< Програмне скидання чипа */

#define INA226_CONFIG_AVG_SHIFT     9U
#define INA226_CONFIG_AVG_MASK      (0x07U << INA226_CONFIG_AVG_SHIFT)

#define INA226_CONFIG_VBUSCT_SHIFT  6U
#define INA226_CONFIG_VBUSCT_MASK   (0x07U << INA226_CONFIG_VBUSCT_SHIFT)

#define INA226_CONFIG_VSHCT_SHIFT   3U
#define INA226_CONFIG_VSHCT_MASK    (0x07U << INA226_CONFIG_VSHCT_SHIFT)

#define INA226_CONFIG_MODE_SHIFT    0U
#define INA226_CONFIG_MODE_MASK     (0x07U << INA226_CONFIG_MODE_SHIFT)

/* ========================================================================== */
/*                 БІТОВІ МАСКИ РЕГІСТРА MASK/ENABLE (0x06)                   */
/* ========================================================================== */

#define INA226_MASK_SOL             (1U << 15)  /**< Перевищення напруги шунта */
#define INA226_MASK_SUL             (1U << 14)  /**< Зниження напруги шунта */
#define INA226_MASK_BOL             (1U << 13)  /**< Перевищення напруги шини */
#define INA226_MASK_BUL             (1U << 12)  /**< Зниження напруги шини */
#define INA226_MASK_POL             (1U << 11)  /**< Перевищення потужності */
#define INA226_MASK_CNVR            (1U << 10)  /**< Дозвіл виводу ALERT за готовністю конверсії */
#define INA226_MASK_AFF             (1U << 4)   /**< Прапор активності сигналу ALERT */
#define INA226_MASK_CVRF            (1U << 3)   /**< Прапор Conversion Ready (готово до зчитування) */
#define INA226_MASK_OVF             (1U << 2)   /**< Прапор математичного переповнення */
#define INA226_MASK_APOL            (1U << 1)   /**< Полярність ALERT (1 = Active-Low, 0 = Active-High) */
#define INA226_MASK_LEN             (1U << 0)   /**< Режим фіксації ALERT (1 = Latched) */

/* ========================================================================== */
/*                            ПЕРЕЛІЧЕННЯ ТА ТИПИ                             */
/* ========================================================================== */

/**
 * @brief Кількість усереднень вимірювань (AVG, біти [11:9]).
 */
typedef enum {
    INA226_AVG_1    = 0,  /**< 1 вибірка (без усереднення) */
    INA226_AVG_4    = 1,  /**< 4 вибірки */
    INA226_AVG_16   = 2,  /**< 16 вибірок */
    INA226_AVG_64   = 3,  /**< 64 вибірки */
    INA226_AVG_128  = 4,  /**< 128 вибірок */
    INA226_AVG_256  = 5,  /**< 256 вибірок */
    INA226_AVG_512  = 6,  /**< 512 вибірок */
    INA226_AVG_1024 = 7   /**< 1024 вибірки */
} ina226_avg_t;

/**
 * @brief Час перетворення напруги (VSHCT/VBUSCT, біти [8:6] та [5:3]).
 */
typedef enum {
    INA226_CONV_TIME_140US  = 0,  /**< 140 мкс */
    INA226_CONV_TIME_204US  = 1,  /**< 204 мкс */
    INA226_CONV_TIME_332US  = 2,  /**< 332 мкс */
    INA226_CONV_TIME_588US  = 3,  /**< 588 мкс */
    INA226_CONV_TIME_1100US = 4,  /**< 1.1 мс (за замовчуванням) */
    INA226_CONV_TIME_2116US = 5,  /**< 2.116 мс */
    INA226_CONV_TIME_4156US = 6,  /**< 4.156 мс */
    INA226_CONV_TIME_8244US = 7   /**< 8.244 мс */
} ina226_conv_time_t;

/**
 * @brief Режими вимірювання (MODE, біти [2:0]).
 */
typedef enum {
    INA226_MODE_POWER_DOWN      = 0,  /**< Режим зниженого енергоспоживання */
    INA226_MODE_SHUNT_TRIGGERED = 1,  /**< Одноразове вимірювання напруги шунта */
    INA226_MODE_BUS_TRIGGERED   = 2,  /**< Одноразове вимірювання напруги шини */
    INA226_MODE_BOTH_TRIGGERED  = 3,  /**< Одноразове вимірювання шунта і шини */
    INA226_MODE_POWER_DOWN2     = 4,  /**< Режим зниженого енергоспоживання */
    INA226_MODE_SHUNT_CONTINUOUS= 5,  /**< Безперервне вимірювання напруги шунта */
    INA226_MODE_BUS_CONTINUOUS  = 6,  /**< Безперервне вимірювання напруги шини */
    INA226_MODE_BOTH_CONTINUOUS = 7   /**< Безперервне вимірювання шунта і шини */
} ina226_mode_t;

/**
 * @brief Статуси виконання операцій драйвера.
 */
typedef enum {
    INA226_OK            = 0,  /**< Успішна операція */
    INA226_ERR_I2C       = 1,  /**< Помилка обміну по I2C */
    INA226_ERR_PARAM     = 2,  /**< Передано некоректні аргументи */
    INA226_ERR_ID        = 3,  /**< Незбіг ID чипа INA226 */
    INA226_ERR_BUSY      = 4,  /**< Конверсію ще не завершено */
    INA226_ERR_TIMEOUT   = 5   /**< Перевищено час очікування */
} ina226_status_t;

/**
 * @brief Опис профілю конфігурації вимірювального тракту.
 */
typedef struct {
    ina226_avg_t       avg;       /**< Кількість усереднень */
    ina226_conv_time_t vshct;     /**< Час конверсії напруги шунта */
    ina226_conv_time_t vbusct;    /**< Час конверсії напруги шини */
    ina226_mode_t      mode;      /**< Режим роботи */
    const char        *name;      /**< Символьна назва профілю */
} ina226_profile_t;

/**
 * @brief Фізичні дані телеметрії INA226.
 */
typedef struct {
    float bus_voltage_v;    /**< Напруга живильної шини, В */
    float shunt_voltage_mv; /**< Падіння напруги на шунті, мВ */
    float current_a;        /**< Струм навантаження, А */
    float power_w;          /**< Споживана потужність, Вт */
    uint16_t raw_bus;       /**< Сире значення з регістра BUSVOLT */
    int16_t  raw_shunt;     /**< Сире значення з регістра SHUNTVOLT */
    int16_t  raw_current;   /**< Сире значення з регістра CURRENT */
    uint16_t raw_power;     /**< Сире значення з регістра POWER */
} ina226_data_t;

/**
 * @brief Стани кінцевого автомата (FSM).
 */
typedef enum {
    INA226_FSM_UNINIT = 0,     /**< Не ініціалізовано */
    INA226_FSM_IDLE,           /**< Готовність до нового вимірювального циклу */
    INA226_FSM_CONFIGURING,    /**< Запис нових конфігураційних профілів */
    INA226_FSM_WAIT_CONV,      /**< Неблокуюче очікування прапорця CVRF */
    INA226_FSM_READ_DATA,      /**< Зчитування регістрів даних */
    INA226_FSM_ERROR           /**< Стан обробки помилок */
} ina226_fsm_state_t;

/**
 * @brief Структурний контекст об'єкта драйвера INA226.
 */
typedef struct {
    uint8_t            i2c_addr;          /**< 7-бітна I2C адреса давача */
    float              r_shunt_ohm;       /**< Опір вимірювального шунта, Ом */
    float              current_lsb_a;     /**< Дискретність вимірювання струму, А/LSB */
    uint16_t           cal_val;           /**< Значення регістра Calibration (0x05) */
    
    ina226_profile_t   active_profile;    /**< Активний профіль конфігурації */
    ina226_fsm_state_t state;             /**< Поточний стан FSM */
    ina226_status_t    last_error;        /**< Код останньої помилки */
    
    uint32_t           conv_start_ms;     /**< Час запуску конверсії (мс) */
    uint32_t           estimated_conv_us;/**< Теоретична тривалість вимірювання (мкс) */
    
    volatile bool      alert_triggered;   /**< Апаратне переривання від лінії ALERT */
    ina226_data_t      latest_data;       /**< Останні обчислені значення */
} ina226_fsm_t;

/* ========================================================================== */
/*                             ПРОТОТИПИ ФУНКЦІЙ                              */
/* ========================================================================== */

ina226_status_t ina226_init(ina226_fsm_t *fsm, uint8_t i2c_addr, float r_shunt, float max_expected_current_a);
ina226_status_t ina226_set_profile(ina226_fsm_t *fsm, const ina226_profile_t *profile);
ina226_status_t ina226_is_conversion_ready(ina226_fsm_t *fsm, bool *ready);
ina226_status_t ina226_read_data(ina226_fsm_t *fsm, ina226_data_t *data);
void            ina226_fsm_process(ina226_fsm_t *fsm, uint32_t current_tick_ms);
void            ina226_on_alert_interrupt(ina226_fsm_t *fsm);
uint32_t        ina226_calculate_conversion_time_us(const ina226_profile_t *profile);

#ifdef __cplusplus
}
#endif

#endif /* INA226_H */
