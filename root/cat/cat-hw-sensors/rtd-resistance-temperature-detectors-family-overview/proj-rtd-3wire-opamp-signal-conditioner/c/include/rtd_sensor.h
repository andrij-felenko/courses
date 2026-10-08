#ifndef RTD_SENSOR_H
#define RTD_SENSOR_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file rtd_sensor.h
 * @brief C-драйвер обробки сигналів 3-провідного резистивного датчика температури (Pt100/Pt1000).
 *
 * Модуль реалізує перетворення коду АЦП у напругу й опір, компенсацію 3-провідної
 * лінії зв'язку, двоточкове калібрування (offset, gain), лінеаризацію за формулою
 * Каллендара — Ван Дюзена та систему самодіагностики вимірювального тракту.
 */

#ifdef __cplusplus
extern "C" {
#endif

/* --- Константи формули Каллендара — Ван Дюзена (IEC 60751 / DIN EN 60751) --- */
#define RTD_CVD_A           3.9083e-3f    /**< Коефіцієнт A (1/°C) */
#define RTD_CVD_B          -5.7750e-7f    /**< Коефіцієнт B (1/°C^2) */
#define RTD_CVD_C          -4.1830e-12f   /**< Коефіцієнт C (1/°C^4) для T < 0 °C */

/* --- Номінальні опори при 0 °C --- */
#define RTD_PT100_R0        100.0f        /**< Опір Pt100 при 0 °C (Ом) */
#define RTD_PT1000_R0       1000.0f       /**< Опір Pt1000 при 0 °C (Ом) */

/* --- Фізичні межі вимірювання за стандартом IEC 60751 --- */
#define RTD_MIN_TEMP_C     -200.0f        /**< Мінімальна робоча температура (°C) */
#define RTD_MAX_TEMP_C      850.0f        /**< Максимальна робоча температура (°C) */

#define RTD_PT100_MIN_RES    18.52f       /**< Опір Pt100 при -200 °C (Ом) */
#define RTD_PT100_MAX_RES   390.48f       /**< Опір Pt100 при +850 °C (Ом) */

/**
 * @brief Статуси діагностики аналогового тракту та вимірювань RTD.
 */
typedef enum {
    RTD_STATUS_OK                = 0,     /**< Вимірювання успішне, параметри в нормі */
    RTD_STATUS_ERR_OPEN_CIRCUIT  = 1,     /**< Обрив вимірювального кола (опір надто високий) */
    RTD_STATUS_ERR_SHORT_CIRCUIT = 2,     /**< Коротке замикання датчика (опір надто низький) */
    RTD_STATUS_ERR_OUT_OF_RANGE  = 3,     /**< Температура вийшла за допустимі межі (-200..+850 °C) */
    RTD_STATUS_ERR_PARAM         = 4      /**< Передано некоректні параметри конфігурації */
} rtd_status_t;

/**
 * @brief Тип резистивного перетворювача температури.
 */
typedef enum {
    RTD_TYPE_PT100  = 0,                  /**< Платиновий термоопір Pt100 (R0 = 100 Ом) */
    RTD_TYPE_PT1000 = 1                   /**< Платиновий термоопір Pt1000 (R0 = 1000 Ом) */
} rtd_type_t;

/**
 * @brief Конструкція налаштувань аналогового вимірювального тракту RTD.
 */
typedef struct {
    float vref_v;                         /**< Опорна напруга АЦП у вольтах (наприклад, 3.3 В) */
    float gain;                           /**< Коефіцієнт підсилення операційного підсилювача / PGA */
    float excitation_current_a;           /**< Струм збудження терморезистора в амперах (наприклад, 0.001 А) */
    uint32_t adc_max_code;                /**< Максимальний цифровий код АЦП (2^N - 1, наприклад 4095 для 12 біт) */
    float r_lead_ohms;                    /**< Опір одного провідника 3-провідної лінії зв'язку (Ом) */
    float r0_ohms;                        /**< Номінальний опір датчика при 0 °C (100.0 або 1000.0 Ом) */
    rtd_type_t type;                      /**< Тип датчика (Pt100 / Pt1000) */
} rtd_config_t;

/**
 * @brief Конструкція двоточкового калібрування аналогового тракту.
 */
typedef struct {
    float offset_ohms;                    /**< Аддитивна похибка зсуву нуля в Омах (Zero Offset) */
    float gain_scale;                     /**< Мультиплікативний коефіцієнт масштабу (Gain Scale, за замовчуванням 1.0) */
} rtd_calib_t;

/* --- Прототипи функцій драйвера RTD --- */

/**
 * @brief Перетворення сирого коду АЦП у напругу на вході АЦП.
 * @param raw_adc Сирий цифровий код з АЦП.
 * @param config Вказівник на структуру конфігурації.
 * @return Напруга в вольтах.
 */
float rtd_adc_to_voltage(uint32_t raw_adc, const rtd_config_t *config);

/**
 * @brief Обчислення фактичного невідкаліброваного опору з виміряної напруги.
 * @param voltage_v Напруга на виході аналогового тракту (В).
 * @param config Вказівник на структуру конфігурації.
 * @return Опір в Омах.
 */
float rtd_voltage_to_raw_resistance(float voltage_v, const rtd_config_t *config);

/**
 * @brief Компенсація опору провідників для 3-провідної схеми підключення.
 * @param raw_resistance Опір вимірювального кола (Ом).
 * @param r_lead_ohms Опір провідника лінії зв'язку (Ом).
 * @return Компенсований опір датчика (Ом).
 */
float rtd_apply_lead_compensation(float raw_resistance, float r_lead_ohms);

/**
 * @brief Застосування двоточкового калібрування нуля та масштабу.
 * @param compensated_resistance Компенсований опір датчика (Ом).
 * @param calib Вказівник на коефіцієнти калібрування.
 * @return Відкалібрований опір датчика (Ом).
 */
float rtd_apply_calibration(float compensated_resistance, const rtd_calib_t *calib);

/**
 * @brief Перевірка опору на обрив, коротке замикання та вихід за межі.
 * @param resistance_ohms Обчислений опір датчика (Ом).
 * @param r0_ohms Номінальний опір датчика при 0 °C (Ом).
 * @return Статус діагностики rtd_status_t.
 */
rtd_status_t rtd_diagnose_resistance(float resistance_ohms, float r0_ohms);

/**
 * @brief Точний аналітичний розрахунок температури за формулою Каллендара — Ван Дюзена.
 * @param resistance_ohms Відкалібрований опір RTD (Ом).
 * @param r0_ohms Номінальний опір датчика при 0 °C (Ом).
 * @param out_temp_c Указівник для збереження результату температури (°C).
 * @return Статус діагностики RTD.
 */
rtd_status_t rtd_resistance_to_temperature_cvd(float resistance_ohms, float r0_ohms, float *out_temp_c);

/**
 * @brief Повний конвеєр обробки від вибірки АЦП до лінеаризованої температури.
 * @param raw_adc Сирий цифровий код АЦП.
 * @param config Параметри аналогового тракту.
 * @param calib Коефіцієнти двоточкового калібрування.
 * @param out_resistance_ohms Указівник для повернення розрахованого опору (Ом).
 * @param out_temp_c Указівник для повернення обчисленої температури (°C).
 * @return Результат обробки та діагностичний статус.
 */
rtd_status_t rtd_process_adc_sample(uint32_t raw_adc, 
                                    const rtd_config_t *config, 
                                    const rtd_calib_t *calib, 
                                    float *out_resistance_ohms, 
                                    float *out_temp_c);

#ifdef __cplusplus
}
#endif

#endif /* RTD_SENSOR_H */
