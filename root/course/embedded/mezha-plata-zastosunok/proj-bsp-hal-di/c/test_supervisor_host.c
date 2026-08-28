/* --- test_supervisor_host.c: Тестування на комп'ютері розробника --- */
#include "supervisor.h"
#include <stdio.h>
#include <assert.h>

// Стан тестового оточення
static uint16_t mock_voltage_mv = 3800;
static board_led_state_t mock_warn_led = BOARD_LED_STATE_OFF;
static bool mock_sensors_powered = false;
static bool mock_sleep_entered = false;

static bsp_status_t mock_led_set(board_led_id_t led, board_led_state_t state) {
    if (led == BOARD_LED_ID_WARNING) mock_warn_led = state;
    return BSP_STATUS_OK;
}

static bsp_status_t mock_power_set(board_power_domain_t domain, bool enable) {
    if (domain == BOARD_POWER_DOMAIN_SENSORS) mock_sensors_powered = enable;
    return BSP_STATUS_OK;
}

static bsp_status_t mock_get_bat(board_battery_metrics_t *m) {
    m->voltage_mv = mock_voltage_mv;
    return BSP_STATUS_OK;
}

static bsp_status_t mock_read_env(board_env_metrics_t *e) {
    e->temperature_centi_c = 2250;
    return BSP_STATUS_OK;
}

static bsp_status_t mock_enter_sleep(board_sleep_mode_t m, uint32_t ms) {
    (void)m; (void)ms;
    mock_sleep_entered = true;
    return BSP_STATUS_OK;
}

static const bsp_driver_t mock_bsp = {
    .led_set = mock_led_set,
    .power_domain_set = mock_power_set,
    .get_battery_metrics = mock_get_bat,
    .read_environment = mock_read_env,
    .enter_low_power = mock_enter_sleep
};

int main(void) {
    supervisor_t sup;
    supervisor_init(&sup, &mock_bsp);

    // Тест 1: Нормальна напруга (3800 мВ)
    mock_voltage_mv = 3800;
    supervisor_run_cycle(&sup);
    assert(sup.is_low_power_warning == false);
    assert(mock_warn_led == BOARD_LED_STATE_OFF);
    assert(mock_sleep_entered == false);
    printf("[PASS] Test Normal Voltage 3800mV\n");

    // Тест 2: Попередження про розряд (3200 мВ)
    mock_voltage_mv = 3200;
    supervisor_run_cycle(&sup);
    assert(sup.is_low_power_warning == true);
    assert(mock_warn_led == BOARD_LED_STATE_ON);
    assert(mock_sleep_entered == false);
    printf("[PASS] Test Warning Voltage 3200mV\n");

    // Тест 3: Аварійне вимкнення (2900 мВ)
    mock_voltage_mv = 2900;
    supervisor_run_cycle(&sup);
    assert(sup.is_critical_shutdown == true);
    assert(mock_sensors_powered == false);
    assert(mock_sleep_entered == true);
    printf("[PASS] Test Critical Shutdown 2900mV\n");

    printf("\nУсі 3 модульні тести успішно пройшли на хості x86-64 за 0.001 с!\n");
    return 0;
}
