// app/app_telemetry.h
#ifndef APP_TELEMETRY_H
#define APP_TELEMETRY_H

#include "bsp/bsp_bme280.h"
#include "services/event_queue.h"

typedef struct {
    bsp_bme280_t* sensor;
    event_queue_t* queue;
    float alert_threshold_c;
} app_telemetry_t;

void app_telemetry_init(app_telemetry_t* app, bsp_bme280_t* sensor, 
                        event_queue_t* queue, float threshold_c);
void app_telemetry_process_event(app_telemetry_t* app, const event_t* evt);

#endif // APP_TELEMETRY_H
