#include <stdint.h>
#include <stdbool.h>

typedef enum {
    INPUT_OK = 0,
    INPUT_ERR_INVALID_PARAM = -1,
    INPUT_ERR_OUT_OF_BOUNDS = -2,
    INPUT_ERR_CALIBRATION_INVALID = -3,
    INPUT_ERR_NVM_READ_WRITE = -4,
    INPUT_ERR_CRC_MISMATCH = -5
} input_error_t;

typedef struct {
    uint16_t adc_min;
    uint16_t adc_center;
    uint16_t adc_max;
    float deadzone_inner;
    float deadzone_outer;
} input_axis_config_t;

typedef struct {
    input_axis_config_t axis_x;
    input_axis_config_t axis_y;
    bool use_radial_deadzone;
    uint16_t crc16;
} input_profile_t;

typedef struct {
    float x;
    float y;
} input_vector_t;

input_error_t input_init(const input_profile_t *profile) {
    if (profile == NULL) {
        return INPUT_ERR_INVALID_PARAM;
    }
    if (profile->axis_x.adc_min >= profile->axis_x.adc_max ||
        profile->axis_y.adc_min >= profile->axis_y.adc_max) {
        return INPUT_ERR_CALIBRATION_INVALID;
    }
    return INPUT_OK;
}
