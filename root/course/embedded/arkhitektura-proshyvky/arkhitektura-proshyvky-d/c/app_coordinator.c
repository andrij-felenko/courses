// app/app_coordinator.c
#include "bsp/bsp_bme280.h"
#include "services/event_queue.h"

typedef struct {
    bsp_bme280_t* sensor;
    event_queue_t* queue;
    float temp_limit_c;
} app_context_t;

static app_context_t g_app;

void app_init(bsp_bme280_t* sensor, event_queue_t* queue, float limit_c) {
    g_app.sensor = sensor;
    g_app.queue = queue;
    g_app.temp_limit_c = limit_c;
}

void app_handle_tick_event(void) {
    bsp_bme280_readings_t readings;
    if (bsp_bme280_measure(g_app.sensor, &readings)) {
        if (readings.temperature_c > g_app.temp_limit_c) {
            sys_event_t alert = {
                .id = EVT_ID_ALARM_OVERTEMP,
                .timestamp_ms = 0,
                .data.sensor_payload = {
                    .temp_c = readings.temperature_c,
                    .pressure_kpa = readings.pressure_hpa / 10.0f
                }
            };
            event_queue_post(g_app.queue, &alert);
        }
    }
}
