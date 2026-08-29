/* app/app_coordinator.h — координатор застосунку.
 * Він єдиний у системі знає всіх одразу: давачі, чергу, автомат режимів
 * і телеметрію. Знає — але тримає їх покажчиками, отриманими ззовні, тож
 * у тесті на комп'ютері розробника ті самі виклики працюють з імітованою
 * шиною й перевіряють бізнес-правила без жодного шматка заліза. */
#ifndef APP_COORDINATOR_H
#define APP_COORDINATOR_H

#include "app/app_fsm.h"
#include "app/app_telemetry.h"
#include "bsp/bsp_accel.h"
#include "bsp/bsp_bme280.h"
#include "bsp/bsp_led.h"
#include "services/event_queue.h"

typedef struct {
    bsp_bme280_t     *env;
    bsp_accel_t      *accel;
    bsp_led_t        *led;
    event_queue_t    *queue;
    float             temp_limit_c;
    float             temp_hysteresis_c;
    float             vibration_limit_g;
    uint32_t          telemetry_window_ms;
    uint32_t          fault_limit;
    telemetry_sink_fn report;
    void             *report_ctx;
} app_coordinator_config_t;

typedef struct {
    app_coordinator_config_t cfg;
    app_fsm_t                fsm;
    app_telemetry_t          telemetry;
    bool                     alarm_active;
    uint32_t                 records_sent;
} app_coordinator_t;

bool app_coordinator_init(app_coordinator_t *app,
                          const app_coordinator_config_t *cfg,
                          uint32_t now_ms);

/* Єдина точка входу з головного циклу: подія — рішення — дія. */
void app_coordinator_dispatch(app_coordinator_t *app, const sys_event_t *evt);

app_state_t app_coordinator_state(const app_coordinator_t *app);
uint32_t    app_coordinator_records_sent(const app_coordinator_t *app);

#endif /* APP_COORDINATOR_H */
