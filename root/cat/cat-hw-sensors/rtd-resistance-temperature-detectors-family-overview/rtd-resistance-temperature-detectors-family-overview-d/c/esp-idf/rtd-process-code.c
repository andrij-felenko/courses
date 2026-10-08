#include <stdio.h>
#include <stdbool.h>
#include "esp_err.h"
#include "driver/spi_master.h"

// Константи раціометричного вимірювача RTD
#define RTD_RREF_OHMS        400.0f  // Опорний резистор Rref для Pt100 (400 Ом)
#define RTD_R0_OHMS          100.0f  // Номінальний опір Pt100 при 0 °C
#define RTD_ALPHA            0.003851f // Температурний коефіцієнт платини IEC 60751

typedef struct {
    float temperature_c;
    float resistance_ohms;
    bool open_circuit_fault;
    bool short_circuit_fault;
} rtd_reading_t;

// Обчислення опору та температури з цифрового коду АЦП (15-бітний ADC)
esp_err_t rtd_process_code(uint16_t adc_code, rtd_reading_t *out_result) {
    if (out_result == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    // Детекція граничних станів (похибки лінії)
    if (adc_code >= 0x7FFF) {
        out_result->open_circuit_fault = true;
        out_result->short_circuit_fault = false;
        out_result->temperature_c = -999.0f;
        return ESP_ERR_INVALID_STATE;
    }
    if (adc_code == 0) {
        out_result->open_circuit_fault = false;
        out_result->short_circuit_fault = true;
        out_result->temperature_c = -999.0f;
        return ESP_ERR_INVALID_STATE;
    }

    out_result->open_circuit_fault = false;
    out_result->short_circuit_fault = false;

    // Раціометричний розрахунок опору: R_RTD = (ADC_code / 32768) * R_ref
    out_result->resistance_ohms = ((float)adc_code / 32768.0f) * RTD_RREF_OHMS;

    // Лінійна апроксимація температури для діапазону -40...+200 °C
    out_result->temperature_c = (out_result->resistance_ohms - RTD_R0_OHMS) / (RTD_R0_OHMS * RTD_ALPHA);

    return ESP_OK;
}
