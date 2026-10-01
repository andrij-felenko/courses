#include "esp_dsp.h"
#include "esp_log.h"

static const char *TAG = "dsp_pie";

esp_err_t calculate_vector_dot_product(const float *vec1, const float *vec2, int len, float *result) {
    // Ініціалізація та перевірка апаратного прискорювача DSP
    esp_err_t ret = dsps_dotprod_f32_init();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації модулів esp-dsp");
        return ret;
    }

    // Скалярний добуток із використанням векторних інструкцій PIE
    ret = dsps_dotprod_f32(vec1, vec2, result, len);
    return ret;
}
