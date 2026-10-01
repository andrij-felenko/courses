#ifndef OPM_SENSOR_H
#define OPM_SENSOR_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define OPM_FILTER_WINDOW_SIZE 16

/**
 * @brief Статус виконання операцій драйвера оптичного ватметра.
 */
typedef enum {
    OPM_OK = 0,
    OPM_ERR_INVALID_PARAM,
    OPM_ERR_WAVELENGTH_OUT_OF_RANGE,
    OPM_ERR_LIDT_EXCEEDED,
    OPM_ERR_NOT_INITIALIZED
} opm_status_t;

/**
 * @brief Точка калібрувальної таблиці спектральної чутливості фотодіода.
 */
typedef struct {
    uint16_t wavelength_nm; /**< Довжина хвилі у нанометрах */
    float sensitivity_a_w;  /**< Спектральна чутливість Rλ у А/Вт */
} opm_calib_point_t;

/**
 * @brief Калібрувальна таблиця фотодетектора.
 */
typedef struct {
    const opm_calib_point_t *points; /**< Вказівник на масив відсортованих точок */
    size_t count;                    /**< Кількість точок у таблиці */
} opm_calib_table_t;

/**
 * @brief Апаратна конфігурація вимірювального тракту OPM.
 */
typedef struct {
    float tia_gain_ohm;         /**< Опір зворотного зв'язку TIA Rf (Ом) */
    float adc_vref_v;           /**< Опорна напруга АЦП Vref (В) */
    uint32_t adc_max_count;     /**< Максимальне значення АЦП (наприклад, 4095 для 12-біт) */
    float lidt_max_power_w;     /**< Поріг оптичного руйнування LIDT (Вт) */
} opm_config_t;

/**
 * @brief Структура стану сенсора оптичної потужності.
 */
typedef struct {
    opm_config_t config;
    opm_calib_table_t calib_table;
    float dark_offset_v;                           /**< Компенсаційна напруга темнового струму (В) */
    uint16_t filter_buffer[OPM_FILTER_WINDOW_SIZE];/**< Кільцевий буфер ковзного усереднення */
    size_t filter_index;
    size_t filter_count;
    uint16_t current_wavelength_nm;               /**< Поточна обрана довжина хвилі (нм) */
    float current_sensitivity_a_w;                /**< Інтерпольована чутливість Rλ (А/Вт) */
    bool is_initialized;
} opm_sensor_t;

/**
 * @brief Ініціалізація драйвера вимірювача оптичної потужності.
 */
opm_status_t opm_init(opm_sensor_t *sensor, const opm_config_t *config, const opm_calib_table_t *calib_table);

/**
 * @brief Процедура калібрування темнового струму (zeroing).
 */
opm_status_t opm_calibrate_dark_offset(opm_sensor_t *sensor, const uint16_t *raw_samples, size_t sample_count);

/**
 * @brief Встановлення робочої довжини хвилі з інтерполяцією чутливості.
 */
opm_status_t opm_set_wavelength(opm_sensor_t *sensor, uint16_t wavelength_nm);

/**
 * @brief Обробка відліку АЦП: фільтрація, віднімання темряви, розрахунок Вт та dBm.
 */
opm_status_t opm_process_adc_sample(opm_sensor_t *sensor, uint16_t raw_adc_sample, float *out_power_w, float *out_power_dbm);

/**
 * @brief Перетворення потужності з Ватів у dBm.
 */
float opm_watts_to_dbm(float power_w);

#endif /* OPM_SENSOR_H */
