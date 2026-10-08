#include <stdint.h>

typedef int32_t q16_t;

// Перетворення float у Q16.16
#define FLOAT_TO_Q16(val) ((q16_t)((val) * 65536.0f))
#define Q16_TO_FLOAT(val) ((float)(val) / 65536.0f)

// API для систем із плаваючою крапкою (float32)
float magnus_saturation_vapor_pressure_f32(float temp, const magnus_params_t *params);
float magnus_dew_point_f32(float temp, float rh, const magnus_params_t *params);
float magnus_absolute_humidity_f32(float temp, float rh, const magnus_params_t *params);

// API для систем з фіксованою крапкою (Q16.16)
q16_t magnus_saturation_vapor_pressure_q16(q16_t temp, const magnus_params_t *params);
q16_t magnus_dew_point_q16(q16_t temp, q16_t rh, const magnus_params_t *params);
q16_t magnus_absolute_humidity_q16(q16_t temp, q16_t rh, const magnus_params_t *params);
