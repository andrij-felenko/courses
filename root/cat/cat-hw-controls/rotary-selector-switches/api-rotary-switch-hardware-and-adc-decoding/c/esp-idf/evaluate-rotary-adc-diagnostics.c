#include <stdint.h>
#include <stdbool.h>

typedef enum {
    SWITCH_STATUS_OK = 0,
    SWITCH_STATUS_BBM_TRANSITION,
    SWITCH_ERROR_SHORT_TO_GND,
    SWITCH_ERROR_SHORT_TO_VCC,
    SWITCH_ERROR_OPEN_CIRCUIT
} switch_diag_status_t;

typedef struct {
    uint8_t position;
    switch_diag_status_t status;
} switch_result_t;

switch_result_t evaluate_rotary_adc_diagnostics(uint16_t raw_adc, uint8_t last_pos) {
    switch_result_t res;
    res.position = last_pos;

    if (raw_adc < 50) {
        res.status = SWITCH_ERROR_SHORT_TO_GND;
    } else if (raw_adc > 4045) {
        res.status = SWITCH_ERROR_SHORT_TO_VCC;
    } else {
        res.status = SWITCH_STATUS_OK;
    }

    return res;
}
