#include "power_adc.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "POWER_ADC";

static bool adc_calibration_init(adc_unit_t unit, adc_channel_t channel, adc_atten_t atten, adc_cali_handle_t *out_handle)
{
    adc_cali_handle_t handle = NULL;
    esp_err_t ret = ESP_FAIL;
    bool calibrated = false;

#if CONFIG_ADC_CALI_SCHEME_LINE_FITTING_SUPPORTED
    if (!calibrated) {
        ESP_LOGI(TAG, "Спроба ініціалізації калібрування методом Line Fitting");
        adc_cali_line_fitting_config_t cali_config = {
            .unit_id = unit,
            .atten = atten,
            .bitwidth = POWER_ADC_BITWIDTH,
        };
        ret = adc_cali_create_scheme_line_fitting(&cali_config, &handle);
        if (ret == ESP_OK) {
            calibrated = true;
        }
    }
#endif

#if CONFIG_ADC_CALI_SCHEME_CURVE_FITTING_SUPPORTED
    if (!calibrated) {
        ESP_LOGI(TAG, "Спроба ініціалізації калібрування методом Curve Fitting");
        adc_cali_curve_fitting_config_t cali_config = {
            .unit_id = unit,
            .chan = channel,
            .atten = atten,
            .bitwidth = POWER_ADC_BITWIDTH,
        };
        ret = adc_cali_create_scheme_curve_fitting(&cali_config, &handle);
        if (ret == ESP_OK) {
            calibrated = true;
        }
    }
#endif

    *out_handle = handle;
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "Калібрування АЦП успішно підключено.");
    } else {
        ESP_LOGW(TAG, "Калібрувальні дані в eFuse відсутні, використовується пряма аппроксимація.");
    }

    return calibrated;
}

esp_err_t power_adc_init(power_adc_config_t *adc_cfg)
{
    if (!adc_cfg) {
        return ESP_ERR_INVALID_ARG;
    }

    adc_cfg->unit = POWER_ADC_UNIT;
    adc_cfg->channel = POWER_ADC_CHANNEL;

    adc_oneshot_unit_init_cfg_t init_config = {
        .unit_id = POWER_ADC_UNIT,
    };
    esp_err_t err = adc_oneshot_new_unit(&init_config, &adc_cfg->adc_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося створити модуль АЦП oneshot: %s", esp_err_to_name(err));
        return err;
    }

    adc_oneshot_chan_cfg_t config = {
        .bitwidth = POWER_ADC_BITWIDTH,
        .atten = POWER_ADC_ATTEN,
    };
    err = adc_oneshot_config_channel(adc_cfg->adc_handle, POWER_ADC_CHANNEL, &config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося налаштувати канал АЦП: %s", esp_err_to_name(err));
        adc_oneshot_del_unit(adc_cfg->adc_handle);
        return err;
    }

    adc_cfg->is_calibrated = adc_calibration_init(POWER_ADC_UNIT, POWER_ADC_CHANNEL, POWER_ADC_ATTEN, &adc_cfg->cali_handle);

    ESP_LOGI(TAG, "Канал АЦП (Unit %d, Channel %d) успішно ініціалізовано.", POWER_ADC_UNIT, POWER_ADC_CHANNEL);
    return ESP_OK;
}

esp_err_t power_adc_read_raw(power_adc_config_t *adc_cfg, int *raw_out)
{
    if (!adc_cfg || !raw_out) {
        return ESP_ERR_INVALID_ARG;
    }

    uint32_t accumulated_raw = 0;
    int single_read = 0;

    for (int i = 0; i < POWER_ADC_SAMPLES_NUM; i++) {
        esp_err_t err = adc_oneshot_read(adc_cfg->adc_handle, adc_cfg->channel, &single_read);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Помилка зчитування АЦП: %s", esp_err_to_name(err));
            return err;
        }
        accumulated_raw += single_read;
    }

    *raw_out = (int)(accumulated_raw / POWER_ADC_SAMPLES_NUM);
    return ESP_OK;
}

esp_err_t power_adc_read_voltage(power_adc_config_t *adc_cfg, uint32_t *voltage_mv_out)
{
    if (!adc_cfg || !voltage_mv_out) {
        return ESP_ERR_INVALID_ARG;
    }

    int raw_val = 0;
    esp_err_t err = power_adc_read_raw(adc_cfg, &raw_val);
    if (err != ESP_OK) {
        return err;
    }

    int pin_voltage_mv = 0;
    if (adc_cfg->is_calibrated) {
        err = adc_cali_raw_to_voltage(adc_cfg->cali_handle, raw_val, &pin_voltage_mv);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Помилка конвертації каліброваного значення АЦП в мВ: %s", esp_err_to_name(err));
            return err;
        }
    } else {
        /* Лінійний обчислювальний фолбек для 12-бітного АЦП та опорної 3.3 В */
        pin_voltage_mv = (raw_val * 3300) / 4095;
    }

    /* Урахування коефіцієнта дільника напруги */
    *voltage_mv_out = (uint32_t)(pin_voltage_mv * VOLTAGE_DIVIDER_RATIO);
    return ESP_OK;
}

esp_err_t power_adc_deinit(power_adc_config_t *adc_cfg)
{
    if (!adc_cfg) {
        return ESP_ERR_INVALID_ARG;
    }

    if (adc_cfg->is_calibrated && adc_cfg->cali_handle) {
#if CONFIG_ADC_CALI_SCHEME_LINE_FITTING_SUPPORTED
        adc_cali_delete_scheme_line_fitting(adc_cfg->cali_handle);
#elif CONFIG_ADC_CALI_SCHEME_CURVE_FITTING_SUPPORTED
        adc_cali_delete_scheme_curve_fitting(adc_cfg->cali_handle);
#endif
    }

    esp_err_t err = adc_oneshot_del_unit(adc_cfg->adc_handle);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Модуль АЦП успішно деініціалізовано.");
    } else {
        ESP_LOGE(TAG, "Помилка видалення юніта АЦП: %s", esp_err_to_name(err));
    }
    return err;
}
