/* app/app_coordinator.c — бізнес-правила логера вібрації.
 * Координатор не чіпає ані регістрів, ані шин: він викликає драйвери BSP
 * і служби. Найнижче, куди він зазирає, — це заголовок драйвера, і саме
 * тому заміна STM32 на ESP32 не змінює тут жодного рядка.
 *
 * Рішення координатор не виконує сам, а публікує подіями: аварія стає
 * подією в черзі й повертається сюди наступним обертом циклу. Завдяки
 * цьому будь-хто — журнал, радіомодуль, дисплей — може її почути, не
 * будучи згаданим у цьому файлі. */
#include "app/app_coordinator.h"

#include <string.h>

static void post(app_coordinator_t *app, event_id_t id, uint32_t now_ms)
{
    const sys_event_t evt = sys_event_make(id, now_ms);
    (void)event_queue_post(app->cfg.queue, &evt);
}

static void post_overtemp(app_coordinator_t *app, uint32_t now_ms,
                          float temp_c, float pressure_hpa)
{
    sys_event_t evt = sys_event_make(EVT_ID_ALARM_OVERTEMP, now_ms);
    evt.data.sensor_payload.temp_c       = temp_c;
    evt.data.sensor_payload.pressure_kpa = pressure_hpa / 10.0f;
    (void)event_queue_post(app->cfg.queue, &evt);
}

static void post_vibration(app_coordinator_t *app, uint32_t now_ms, float peak_g)
{
    sys_event_t evt = sys_event_make(EVT_ID_ALARM_VIBRATION, now_ms);
    evt.data.vibration_payload.peak_g = peak_g;
    (void)event_queue_post(app->cfg.queue, &evt);
}

static void post_fault(app_coordinator_t *app, uint32_t now_ms,
                       hal_i2c_status_t status, uint8_t dev_addr)
{
    sys_event_t evt = sys_event_make(EVT_ID_SENSOR_FAULT, now_ms);
    evt.data.fault_payload.code        = (int32_t)status;
    evt.data.fault_payload.device_addr = dev_addr;
    (void)event_queue_post(app->cfg.queue, &evt);
}

bool app_coordinator_init(app_coordinator_t *app,
                          const app_coordinator_config_t *cfg,
                          uint32_t now_ms)
{
    if (app == 0 || cfg == 0 || cfg->queue == 0 || cfg->env == 0) {
        return false;
    }

    memset(app, 0, sizeof *app);
    app->cfg = *cfg;

    if (app->cfg.temp_hysteresis_c <= 0.0f) {
        app->cfg.temp_hysteresis_c = 1.0f;
    }

    app_fsm_init(&app->fsm, cfg->fault_limit);
    app_telemetry_init(&app->telemetry, cfg->telemetry_window_ms, now_ms);
    app->alarm_active = false;
    return true;
}

/* Одне повне опитування давачів. Повертає false, якщо хоч один відмовив:
 * тоді ми не змішуємо свіжу температуру з торішньою вібрацією, а чесно
 * рахуємо цикл невдалим. */
static bool sample_sensors(app_coordinator_t *app, uint32_t now_ms)
{
    bsp_bme280_readings_t env;
    if (!bsp_bme280_measure(app->cfg.env, &env)) {
        app_telemetry_add_fault(&app->telemetry);
        post_fault(app, now_ms, bsp_bme280_last_error(app->cfg.env), 0u);
        return false;
    }

    float vibration_g = 0.0f;
    if (app->cfg.accel != 0) {
        bsp_accel_sample_t accel;
        if (!bsp_accel_read(app->cfg.accel, &accel)) {
            app_telemetry_add_fault(&app->telemetry);
            post_fault(app, now_ms, bsp_accel_last_error(app->cfg.accel), 0u);
            return false;
        }
        vibration_g = bsp_accel_vibration_g(&accel);
    }

    app_telemetry_add_sample(&app->telemetry, now_ms,
                             env.temperature_c, env.humidity_rh,
                             env.pressure_hpa, vibration_g);

    post(app, EVT_ID_SENSOR_DATA_READY, now_ms);

    /* Пороги. Тривога піднімається один раз, а знімається лише коли
     * температура впала нижче за поріг на гістерезис: без цього логер
     * на межі 65.0 °C сипав би подіями сотнями разів на хвилину. */
    const bool too_hot = env.temperature_c > app->cfg.temp_limit_c;
    const bool shaking = vibration_g > app->cfg.vibration_limit_g;

    if (!app->alarm_active) {
        if (too_hot) {
            app->alarm_active = true;
            post_overtemp(app, now_ms, env.temperature_c, env.pressure_hpa);
        } else if (shaking) {
            app->alarm_active = true;
            post_vibration(app, now_ms, vibration_g);
        }
    } else {
        const bool cooled =
            env.temperature_c < (app->cfg.temp_limit_c - app->cfg.temp_hysteresis_c);
        if (cooled && !shaking) {
            app->alarm_active = false;
            post(app, EVT_ID_ALARM_CLEARED, now_ms);
        }
    }

    /* Закриття вікна телеметрії. Запис віддаємо приймачеві, якого дав порт:
     * на платі це передавач UART, на комп'ютері розробника — друк у консоль. */
    if (app_telemetry_window_elapsed(&app->telemetry, now_ms)) {
        telemetry_record_t record;
        if (app_telemetry_close_window(&app->telemetry, now_ms, &record) &&
            app->cfg.report != 0) {
            app->cfg.report(app->cfg.report_ctx, &record);
            app->records_sent++;
        }
    }
    return true;
}

static void apply_action(app_coordinator_t *app, app_action_t action, uint32_t now_ms)
{
    switch (action) {

    case APP_ACTION_START_SAMPLING:
        bsp_led_set_mode(app->cfg.led, BSP_LED_BLINK_SLOW);
        app_telemetry_init(&app->telemetry, app->cfg.telemetry_window_ms, now_ms);
        break;

    case APP_ACTION_STOP_SAMPLING:
        bsp_led_set_mode(app->cfg.led, BSP_LED_OFF);
        break;

    case APP_ACTION_SAMPLE_SENSORS:
        (void)sample_sensors(app, now_ms);
        break;

    case APP_ACTION_RAISE_ALARM:
        bsp_led_set_mode(app->cfg.led, BSP_LED_BLINK_FAST);
        break;

    case APP_ACTION_CLEAR_ALARM:
        bsp_led_set_mode(app->cfg.led, BSP_LED_BLINK_SLOW);
        break;

    case APP_ACTION_ENTER_FAULT:
        /* Давач не відповідає. Світлодіод горить рівно — це видно здалеку
         * і відрізняється від миготіння штатної роботи. */
        bsp_led_set_mode(app->cfg.led, BSP_LED_ON);
        app->alarm_active = false;
        break;

    case APP_ACTION_RECOVER:
        bsp_led_set_mode(app->cfg.led, BSP_LED_BLINK_SLOW);
        break;

    case APP_ACTION_NONE:
    default:
        break;
    }
}

void app_coordinator_dispatch(app_coordinator_t *app, const sys_event_t *evt)
{
    if (app == 0 || evt == 0) {
        return;
    }

    const app_action_t action = app_fsm_dispatch(&app->fsm, evt);
    apply_action(app, action, evt->timestamp_ms);

    /* Індикація живе на тіку: миготіння не має залежати від того, чи
     * встиг давач відповісти цього оберту. */
    if (evt->id == EVT_ID_TICK_100MS) {
        bsp_led_tick(app->cfg.led, evt->timestamp_ms);
    }
}

app_state_t app_coordinator_state(const app_coordinator_t *app)
{
    return (app != 0) ? app_fsm_state(&app->fsm) : APP_STATE_BOOT;
}

uint32_t app_coordinator_records_sent(const app_coordinator_t *app)
{
    return (app != 0) ? app->records_sent : 0u;
}
