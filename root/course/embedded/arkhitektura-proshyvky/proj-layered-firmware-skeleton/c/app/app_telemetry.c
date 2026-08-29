// app/app_telemetry.c
#include "app/app_telemetry.h"

#include <stddef.h>

static void emit(app_telemetry_t* app, event_type_t type, uint32_t ts_ms, float sensor_val,
                 int32_t error_code)
{
    event_t evt;
    evt.type = type;
    evt.timestamp_ms = ts_ms;
    if (type == EVT_SENSOR_FAULT) {
        evt.payload.error_code = error_code;
    } else {
        evt.payload.sensor_val = sensor_val;
    }
    (void)event_queue_push(app->queue, &evt);
}

static void take_sample(app_telemetry_t* app, uint32_t ts_ms)
{
    bsp_bme280_data_t data;
    if (!bsp_bme280_read(app->sensor, &data)) {
        // Крок 3 трасування: політику реакції на збій ухвалює саме цей шар.
        if (app->consecutive_failures < UINT8_MAX) {
            app->consecutive_failures++;
        }
        if (app->consecutive_failures >= APP_SENSOR_FAULT_LIMIT) {
            emit(app, EVT_SENSOR_FAULT, ts_ms, 0.0f, (int32_t)app->consecutive_failures);
            app->faults_raised++;
            // Лічильник не обнуляємо тут: його зніме служба живлення, коли
            // справді перезапустить давач. Інакше тривога загубиться в циклі.
        }
        return;
    }

    app->consecutive_failures = 0u;
    app->has_last_reading = true;
    app->last_reading = data;
    app->samples_taken++;

    if (data.temperature_c > app->alert_threshold_c) {
        emit(app, EVT_ALERT_THRESHOLD, ts_ms, data.temperature_c, 0);
        app->alerts_raised++;
    }
}

void app_telemetry_init(app_telemetry_t* app, bsp_bme280_t* sensor, event_queue_t* queue,
                        float threshold_c, uint16_t sample_period_ticks)
{
    if (!app) return;
    app->sensor = sensor;
    app->queue = queue;
    app->alert_threshold_c = threshold_c;
    app->sample_period_ticks = (sample_period_ticks == 0u) ? 1u : sample_period_ticks;
    app->ticks_since_sample = 0u;
    app->consecutive_failures = 0u;
    app->has_last_reading = false;
    app->last_reading.temperature_c = 0.0f;
    app->last_reading.humidity_percent = 0.0f;
    app->last_reading.pressure_hpa = 0.0f;
    app->samples_taken = 0u;
    app->alerts_raised = 0u;
    app->faults_raised = 0u;
}

void app_telemetry_process_event(app_telemetry_t* app, const event_t* evt)
{
    // Відсутній дескриптор давача — не привід мовчати: bsp_bme280_read віддасть
    // на нього false, і подія несправності піде звичайним шляхом.
    if (!app || !evt || !app->queue) return;

    switch (evt->type) {
        case EVT_TIMER_TICK:
            app->ticks_since_sample++;
            if (app->ticks_since_sample >= app->sample_period_ticks) {
                app->ticks_since_sample = 0u;
                take_sample(app, evt->timestamp_ms);
            }
            break;

        case EVT_SENSOR_TRIGGER:
            app->ticks_since_sample = 0u;
            take_sample(app, evt->timestamp_ms);
            break;

        default:
            // Тривога, несправність, звільнення передавача — не наша справа.
            break;
    }
}

void app_telemetry_event_handler(void* context, const event_t* evt)
{
    app_telemetry_process_event((app_telemetry_t*)context, evt);
}

void app_telemetry_set_sensor(app_telemetry_t* app, bsp_bme280_t* sensor)
{
    if (!app) return;
    app->sensor = sensor;
}

void app_telemetry_notify_recovered(app_telemetry_t* app)
{
    if (!app) return;
    app->consecutive_failures = 0u;
}

bool app_telemetry_last_reading(const app_telemetry_t* app, bsp_bme280_data_t* out)
{
    if (!app || !out || !app->has_last_reading) return false;
    *out = app->last_reading;
    return true;
}
