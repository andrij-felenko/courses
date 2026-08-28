/* --- supervisor.h: Бізнес-логіка (100% переносний код) --- */
#ifndef SUPERVISOR_H
#define SUPERVISOR_H

#include "bsp_interface.h"

typedef struct {
    bsp_status_t (*led_set)(board_led_id_t led, board_led_state_t state);
    bsp_status_t (*power_domain_set)(board_power_domain_t domain, bool enable);
    bsp_status_t (*get_battery_metrics)(board_battery_metrics_t *metrics);
    bsp_status_t (*read_environment)(board_env_metrics_t *env);
    bsp_status_t (*enter_low_power)(board_sleep_mode_t mode, uint32_t timeout_ms);
} bsp_driver_t;

typedef struct {
    const bsp_driver_t *bsp;
    bool is_low_power_warning;
    bool is_critical_shutdown;
} supervisor_t;

void supervisor_init(supervisor_t *ctx, const bsp_driver_t *bsp);
void supervisor_run_cycle(supervisor_t *ctx);

#endif /* SUPERVISOR_H */
