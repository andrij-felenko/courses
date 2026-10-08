#include <stdio.h>
#include <math.h>
#include <stdbool.h>
#include "esp_err.h"
#include "esp_log.h"

static const char *TAG = "RTD_AFE";

// Коефіцієнти Каллендара — Ван Дюзена за стандартом IEC 60751
#define RTD_CVD_A      3.9083e-3f
#define RTD_CVD_B      -5.775e-7f

typedef struct {
    float r_ref;           // Опір опорного резистора Rref (400.0 Ом для Pt100)
    float r0;              // Номінальний опір сенсора R0 (100.0 Ом або 1000.0 Ом)
    uint8_t adc_bits;      // Розрядність АЦП (15 біт для MAX31865 або 24 біт)
} rtd_afe_config_t;

typedef struct {
    float temperature_c;
    float resistance_ohms;
    bool open_circuit;
    bool short_circuit;
} rtd_afe_result_t;

// Програмний розрахунок температури з діагностикою аварійних станів
esp_err_t rtd_afe_read_temperature(const rtd_afe_config_t *config, uint32_t raw_adc_code, rtd_afe_result_t *result) {
    if (!config || !result) {
        return ESP_ERR_INVALID_ARG;
    }

    uint32_t max_code = (1UL << config->adc_bits) - 1;

    // 1. Апаратна діагностика за граничними значеннями коду АЦП
    if (raw_adc_code >= max_code) {
        result->open_circuit = true;
        result->short_circuit = false;
        result->temperature_c = NAN;
        result->resistance_ohms = INFINITY;
        ESP_LOGE(TAG, "Помилка лінії: виявлено обрив кола (Open Circuit)");
        return ESP_ERR_INVALID_STATE;
    }

    if (raw_adc_code == 0) {
        result->open_circuit = false;
        result->short_circuit = true;
        result->temperature_c = NAN;
        result->resistance_ohms = 0.0f;
        ESP_LOGE(TAG, "Помилка лінії: виявлено коротке замикання (Short Circuit)");
        return ESP_ERR_INVALID_STATE;
    }

    result->open_circuit = false;
    result->short_circuit = false;

    // 2. Раціометричний розрахунок опору: R_RTD = (Code / MaxCode) * R_ref
    float r_rtd = ((float)raw_adc_code / (float)max_code) * config->r_ref;
    result->resistance_ohms = r_rtd;

    // 3. Точна квадратична лінеаризація за рівнянням Каллендара — Ван Дюзена (T >= 0 °C)
    float a = RTD_CVD_A;
    float b = RTD_CVD_B;
    float r0 = config->r0;

    float discriminant = (r0 * a) * (r0 * a) - 4.0f * (r0 * b) * (r0 - r_rtd);
    if (discriminant < 0.0f) {
        result->temperature_c = NAN;
        return ESP_ERR_FAIL;
    }

    float temp = (-r0 * a + sqrtf(discriminant)) / (2.0f * r0 * b);
    result->temperature_c = temp;

    return ESP_OK;
}
