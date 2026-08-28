// ============================================================================
// test_limp_controller.c - C99 Модульні тести
// ============================================================================
#include <stdio.h>
#include <assert.h>
#include <math.h>
#include "limp_controller.h"

static void test_normal_to_throttled_transition(void) {
    limp_controller_t ctrl;
    limp_config_t cfg = {
        .temp_warn_c = 90.0f,
        .temp_crit_c = 105.0f,
        .temp_fatal_c = 115.0f,
        .temp_hysteresis_c = 8.0f,
        .cell_volt_warn_v = 3.3f,
        .cell_volt_crit_v = 3.0f,
        .nominal_current_max_a = 80.0f,
        .limp_l1_current_max_a = 40.0f,
        .limp_l2_current_max_a = 28.0f,
        .min_dwell_time_ms = 1000
    };
    limp_controller_init(&ctrl, &cfg);

    limp_sensor_telemetry_t telem = {
        .mosfet_temp_c = 95.0f, // Перевищення T_warn (90C)
        .motor_temp_c = 45.0f,
        .bus_voltage_v = 24.0f,
        .min_cell_voltage_v = 3.8f,
        .total_current_a = 35.0f,
        .current_sensors_healthy = true,
        .telemetry_link_healthy = true,
        .timestamp_ms = 100
    };

    limp_control_outputs_t out;
    limp_controller_step(&ctrl, &telem, &out);

    assert(out.current_state == LIMP_STATE_THROTTLED);
    assert(out.max_allowed_current_a > 65.0f && out.max_allowed_current_a < 68.0f);
    assert(out.target_pwm_freq_hz == 16000);
    assert(out.enable_tier3_payload == true);
    printf("[PASS] test_normal_to_throttled_transition\n");
}

static void test_sensor_fault_immediate_l2(void) {
    limp_controller_t ctrl;
    limp_config_t cfg = {
        .temp_warn_c = 90.0f, .temp_crit_c = 105.0f, .temp_fatal_c = 115.0f,
        .temp_hysteresis_c = 8.0f, .cell_volt_warn_v = 3.3f, .cell_volt_crit_v = 3.0f,
        .nominal_current_max_a = 80.0f, .limp_l1_current_max_a = 40.0f,
        .limp_l2_current_max_a = 28.0f, .min_dwell_time_ms = 1000
    };
    limp_controller_init(&ctrl, &cfg);

    limp_sensor_telemetry_t telem = {
        .mosfet_temp_c = 40.0f,
        .bus_voltage_v = 24.0f,
        .min_cell_voltage_v = 3.9f,
        .total_current_a = 15.0f,
        .current_sensors_healthy = false, // Відмова сенсора струму!
        .telemetry_link_healthy = true,
        .timestamp_ms = 200
    };

    limp_control_outputs_t out;
    limp_controller_step(&ctrl, &telem, &out);

    assert(out.current_state == LIMP_STATE_L2);
    assert(out.max_allowed_current_a == 28.0f);
    assert(out.enable_tier2_sbc == false); // SBC знеструмлено
    assert(out.enable_tier3_payload == false);
    assert(out.active_primary_dtc == DTC_CODE_CURRENT_SENSE_FAIL);
    printf("[PASS] test_sensor_fault_immediate_l2\n");
}

static void test_hysteresis_and_dwell_timing(void) {
    limp_controller_t ctrl;
    limp_config_t cfg = {
        .temp_warn_c = 90.0f, .temp_crit_c = 105.0f, .temp_fatal_c = 115.0f,
        .temp_hysteresis_c = 8.0f, .cell_volt_warn_v = 3.3f, .cell_volt_crit_v = 3.0f,
        .nominal_current_max_a = 80.0f, .limp_l1_current_max_a = 40.0f,
        .limp_l2_current_max_a = 28.0f, .min_dwell_time_ms = 1000
    };
    limp_controller_init(&ctrl, &cfg);

    limp_sensor_telemetry_t telem = {
        .mosfet_temp_c = 92.0f, .bus_voltage_v = 24.0f, .min_cell_voltage_v = 3.8f,
        .current_sensors_healthy = true, .telemetry_link_healthy = true, .timestamp_ms = 0
    };
    limp_control_outputs_t out;
    limp_controller_step(&ctrl, &telem, &out);
    assert(out.current_state == LIMP_STATE_THROTTLED);

    // Температура впала нижче порога (80C < 90 - 8 = 82C), але час 500мс < 1000мс
    telem.mosfet_temp_c = 80.0f;
    telem.timestamp_ms = 500;
    limp_controller_step(&ctrl, &telem, &out);
    assert(out.current_state == LIMP_STATE_THROTTLED); // Захист Dwell діє!

    // Час минув (1200мс > 1000мс) -> повернення в Normal
    telem.timestamp_ms = 1200;
    limp_controller_step(&ctrl, &telem, &out);
    assert(out.current_state == LIMP_STATE_NORMAL);
    assert(out.max_allowed_current_a == 80.0f);
    printf("[PASS] test_hysteresis_and_dwell_timing\n");
}

int main(void) {
    test_normal_to_throttled_transition();
    test_sensor_fault_immediate_l2();
    test_hysteresis_and_dwell_timing();
    printf("Всі C99 тести перевірки інваріантів успішно пройдено!\n");
    return 0;
}
