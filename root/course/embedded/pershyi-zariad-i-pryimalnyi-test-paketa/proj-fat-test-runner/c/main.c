#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_CELLS 16
#define MAX_NTC   4

typedef enum {
    FAT_STATE_IDLE,
    FAT_STATE_OCV_CHECK,
    FAT_STATE_WELD_RESISTANCE_TEST,
    FAT_STATE_PRECHARGE_QUALIFICATION,
    FAT_STATE_CC_CV_CHARGE_TEST,
    FAT_STATE_SAFETY_TRIP_VERIFICATION,
    FAT_STATE_PASSED,
    FAT_STATE_FAILED
} fat_state_t;

typedef enum {
    FAT_ERR_NONE = 0,
    FAT_ERR_OCV_OUT_OF_BOUNDS,
    FAT_ERR_CELL_IMBALANCE_TOO_HIGH,
    FAT_ERR_WELD_RESISTANCE_EXCESSIVE,
    FAT_ERR_TEMPERATURE_GRADIENT_HIGH,
    FAT_ERR_OVERVOLTAGE_PROTECTION_FAILED,
    FAT_ERR_COMMUNICATION_TIMEOUT
} fat_error_t;

typedef struct {
    uint16_t min_cell_mv;
    uint16_t max_cell_mv;
    uint16_t max_imbalance_mv;
    uint32_t max_weld_resistance_uohm;
    int16_t  max_temp_c;
    int16_t  max_temp_gradient_c;
    uint16_t ovp_trip_threshold_mv;
} fat_limits_t;

typedef struct {
    uint8_t  cell_count;
    uint8_t  ntc_count;
    uint16_t cell_mv[MAX_CELLS];
    int16_t  temp_c[MAX_NTC];
    uint32_t weld_res_uohm[MAX_CELLS];
    int32_t  current_ma;
    bool     bms_chg_mosfet_active;
    bool     bms_dsg_mosfet_active;
} pack_telemetry_t;

typedef struct {
    fat_state_t      state;
    fat_error_t      last_error;
    fat_limits_t     limits;
    pack_telemetry_t telemetry;
    uint32_t         step_timer_ms;
} fat_runner_t;

void fat_runner_init(fat_runner_t *runner, const fat_limits_t *limits) {
    memset(runner, 0, sizeof(fat_runner_t));
    runner->state = FAT_STATE_IDLE;
    runner->limits = *limits;
}

fat_error_t fat_evaluate_ocv(fat_runner_t *runner) {
    uint16_t min_v = 0xFFFF;
    uint16_t max_v = 0;
    
    for (uint8_t i = 0; i < runner->telemetry.cell_count; ++i) {
        uint16_t v = runner->telemetry.cell_mv[i];
        if (v < runner->limits.min_cell_mv || v > runner->limits.max_cell_mv) {
            return FAT_ERR_OCV_OUT_OF_BOUNDS;
        }
        if (v < min_v) min_v = v;
        if (v > max_v) max_v = v;
    }
    
    if ((max_v - min_v) > runner->limits.max_imbalance_mv) {
        return FAT_ERR_CELL_IMBALANCE_TOO_HIGH;
    }
    return FAT_ERR_NONE;
}

fat_error_t fat_evaluate_weld_resistance(fat_runner_t *runner) {
    for (uint8_t i = 0; i < runner->telemetry.cell_count; ++i) {
        if (runner->telemetry.weld_res_uohm[i] > runner->limits.max_weld_resistance_uohm) {
            return FAT_ERR_WELD_RESISTANCE_EXCESSIVE;
        }
    }
    return FAT_ERR_NONE;
}

fat_error_t fat_evaluate_thermal(fat_runner_t *runner) {
    int16_t min_t = 30000;
    int16_t max_t = -30000;
    
    for (uint8_t i = 0; i < runner->telemetry.ntc_count; ++i) {
        int16_t t = runner->telemetry.temp_c[i];
        if (t > runner->limits.max_temp_c) {
            return FAT_ERR_TEMPERATURE_GRADIENT_HIGH;
        }
        if (t < min_t) min_t = t;
        if (t > max_t) max_t = t;
    }
    
    if ((max_t - min_t) > runner->limits.max_temp_gradient_c) {
        return FAT_ERR_TEMPERATURE_GRADIENT_HIGH;
    }
    return FAT_ERR_NONE;
}

void fat_runner_tick(fat_runner_t *runner, uint32_t dt_ms) {
    runner->step_timer_ms += dt_ms;
    
    switch (runner->state) {
        case FAT_STATE_IDLE:
            runner->state = FAT_STATE_OCV_CHECK;
            runner->step_timer_ms = 0;
            break;
            
        case FAT_STATE_OCV_CHECK: {
            fat_error_t err = fat_evaluate_ocv(runner);
            if (err != FAT_ERR_NONE) {
                runner->last_error = err;
                runner->state = FAT_STATE_FAILED;
            } else {
                runner->state = FAT_STATE_WELD_RESISTANCE_TEST;
                runner->step_timer_ms = 0;
            }
            break;
        }
        
        case FAT_STATE_WELD_RESISTANCE_TEST: {
            fat_error_t err = fat_evaluate_weld_resistance(runner);
            if (err != FAT_ERR_NONE) {
                runner->last_error = err;
                runner->state = FAT_STATE_FAILED;
            } else {
                runner->state = FAT_STATE_CC_CV_CHARGE_TEST;
                runner->step_timer_ms = 0;
            }
            break;
        }
        
        case FAT_STATE_CC_CV_CHARGE_TEST: {
            fat_error_t th_err = fat_evaluate_thermal(runner);
            if (th_err != FAT_ERR_NONE) {
                runner->last_error = th_err;
                runner->state = FAT_STATE_FAILED;
                break;
            }
            if (runner->step_timer_ms >= 5000) {
                runner->state = FAT_STATE_SAFETY_TRIP_VERIFICATION;
                runner->step_timer_ms = 0;
            }
            break;
        }
        
        case FAT_STATE_SAFETY_TRIP_VERIFICATION: {
            if (!runner->telemetry.bms_chg_mosfet_active) {
                runner->state = FAT_STATE_PASSED;
            } else if (runner->step_timer_ms > 2000) {
                runner->last_error = FAT_ERR_OVERVOLTAGE_PROTECTION_FAILED;
                runner->state = FAT_STATE_FAILED;
            }
            break;
        }
        
        case FAT_STATE_PASSED:
        case FAT_STATE_FAILED:
        default:
            break;
    }
}
