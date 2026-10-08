#ifndef POWER_ADC_H
#define POWER_ADC_H

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

#ifdef __cplusplus
extern "C" {
#endif

#define POWER_ADC_UNIT            ADC_UNIT_1
#define POWER_ADC_CHANNEL         ADC_CHANNEL_2   /* GPIO 3 на ESP32-S3 */
#define POWER_ADC_ATTEN           ADC_ATTEN_DB_12 /* Діапазон 0..3.3 В */
#define POWER_ADC_BITWIDTH        ADC_BITWIDTH_DEFAULT /* 12-біт (0..4095) */
#define POWER_ADC_SAMPLES_NUM     32    /* Кількість вибірок для усреднення */
#define VOLTAGE_DIVIDER_RATIO     2.0f  /* Коефіцієнт дільника напруги (1:1 дільник) */

/**
 * @brief Структура конфігурації та стану монітора напруги АЦП
 */
typedef struct {
    adc_oneshot_unit_handle_t adc_handle;
    adc_cali_handle_t cali_handle;
    bool is_calibrated;
    adc_unit_t unit;
    adc_channel_t channel;
} power_adc_config_t;

/**
 * @brief Ініціалізація та калібрування каналу АЦП для вимірювання напруги.
 *
 * @param adc_cfg Указник на структуру power_adc_config_t
 * @return esp_err_t ESP_OK у разі успішної ініціалізації
 */
esp_err_t power_adc_init(power_adc_config_t *adc_cfg);

/**
 * @brief Зчитування усредненого сирого значення АЦП з вибірок.
 *
 * @param adc_cfg Указник на налаштований модуль АЦП
 * @param raw_out Указник для збереження значення (0..4095)
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t power_adc_read_raw(power_adc_config_t *adc_cfg, int *raw_out);

/**
 * @brief Зчитування каліброваної значення напруги в мілівольтах (мВ).
 *
 * @param adc_cfg Указник на налаштований модуль АЦП
 * @param voltage_mv_out Указник для збереження обчисленої напруги в мВ
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t power_adc_read_voltage(power_adc_config_t *adc_cfg, uint32_t *voltage_mv_out);

/**
 * @brief Деініціалізація АЦП та звільнення схем калібрування.
 *
 * @param adc_cfg Указник на структуру АЦП
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t power_adc_deinit(power_adc_config_t *adc_cfg);

#ifdef __cplusplus
}
#endif

#endif /* POWER_ADC_H */
