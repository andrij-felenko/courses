// C реалізація перевірки стану FOC та автоматичного захисту
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    float encoder_offset_rad;
    float max_phase_current_a;
    float max_temp_celsius;
    bool is_calibrated;
} bldc_config_t;

typedef enum {
    SERVO_OK = 0,
    ERR_ENCODER_OFFSET = 1,
    ERR_OVERCURRENT = 2,
    ERR_OVERTEMP = 3
} servo_error_t;

servo_error_t bldc_verify_safety(float current_a, float temp_c, const bldc_config_t *cfg) {
    if (!cfg->is_calibrated) {
        return ERR_ENCODER_OFFSET;
    }
    if (current_a > cfg->max_phase_current_a) {
        return ERR_OVERCURRENT;
    }
    if (temp_c > cfg->max_temp_celsius) {
        return ERR_OVERTEMP;
    }
    return SERVO_OK;
}
