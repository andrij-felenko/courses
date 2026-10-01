#ifndef ACS712_DRIVER_H
#define ACS712_DRIVER_H

#include <stdbool.h>
#include "esp_err.h"
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"

typedef enum {
    ACS712_TYPE_05B = 0, // 185 mV/A
    ACS712_TYPE_20A,     // 100 mV/A
    ACS712_TYPE_30A      // 66 mV/A
} acs712_type_t;

typedef struct {
    adc_channel_t adc_channel;
    acs712_type_t type;
    gpio_num_t relay_gpio;
    float vcc;
    float overcurrent_limit_a;
    float hysteresis_a;
} acs712_config_t;

typedef struct {
    adc_oneshot_unit_handle_t adc_handle;
    adc_channel_t adc_channel;
    float sensitivity_v_a;
    float zero_voltage;
    gpio_num_t relay_gpio;
    float overcurrent_limit_a;
    float hysteresis_a;
    bool relay_state;
} acs712_handle_t;

esp_err_t acs712_init(acs712_handle_t *handle, const acs712_config_t *config);
esp_err_t acs712_calibrate_zero(acs712_handle_t *handle, int num_samples);
esp_err_t acs712_read_current_dc(acs712_handle_t *handle, float *out_current);
esp_err_t acs712_read_current_rms(acs712_handle_t *handle, float frequency_hz, float *out_rms);
esp_err_t acs712_check_protection(acs712_handle_t *handle, float current_rms);

#endif // ACS712_DRIVER_H
