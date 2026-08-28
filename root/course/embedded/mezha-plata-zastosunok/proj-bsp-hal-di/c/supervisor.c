/* --- supervisor.c --- */
#include "supervisor.h"

void supervisor_init(supervisor_t *ctx, const bsp_driver_t *bsp) {
    ctx->bsp = bsp;
    ctx->is_low_power_warning = false;
    ctx->is_critical_shutdown = false;
}

void supervisor_run_cycle(supervisor_t *ctx) {
    if (!ctx || !ctx->bsp) return;

    board_battery_metrics_t bat = {0};
    bsp_status_t st = ctx->bsp->get_battery_metrics(&bat);
    if (st != BSP_STATUS_OK) {
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_ON);
        return;
    }

    // Критичний поріг розряду (3000 мВ): аварійний сон
    if (bat.voltage_mv < 3000) {
        ctx->is_critical_shutdown = true;
        ctx->bsp->led_set(BOARD_LED_ID_SYSTEM_STATUS, BOARD_LED_STATE_OFF);
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_ON);
        ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_SENSORS, false);
        ctx->bsp->enter_low_power(BOARD_SLEEP_MODE_DEEP, 3600000); // 1 година
        return;
    }

    // Попереджувальний поріг розряду (3300 мВ)
    if (bat.voltage_mv < 3300) {
        ctx->is_low_power_warning = true;
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_ON);
    } else {
        ctx->is_low_power_warning = false;
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_OFF);
    }

    // Штатний цикл збору даних
    ctx->bsp->led_set(BOARD_LED_ID_SYSTEM_STATUS, BOARD_LED_STATE_ON);
    ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_SENSORS, true);

    board_env_metrics_t env = {0};
    ctx->bsp->read_environment(&env);

    ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_SENSORS, false);
    ctx->bsp->led_set(BOARD_LED_ID_SYSTEM_STATUS, BOARD_LED_STATE_OFF);
}
