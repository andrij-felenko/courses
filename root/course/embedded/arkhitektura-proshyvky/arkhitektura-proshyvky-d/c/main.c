/* main.c — головний диспетчер прошивки.
 * Увесь файл не залежить від плати: board_init() підставляє або справжній
 * STM32F401, або імітацію на комп'ютері розробника, а цикл лишається тим
 * самим. Ніяких HAL_Delay і порожніх очікувань: коли черга спорожніла,
 * ядро спить до найближчого переривання. */
#include "app/app_coordinator.h"
#include "bsp/bsp_led.h"
#include "hal/hal_time.h"
#include "include/board.h"
#include "include/sys_config.h"

/* Уся пам'ять статична й порахована на етапі компіляції: у прошивці немає
 * купи, тож немає й способу впасти через її фрагментацію на шостому місяці. */
static sys_event_t          g_event_storage[SYS_EVENT_QUEUE_CAPACITY];
static event_queue_t        g_events;
static bsp_bme280_storage_t g_env_storage;
static bsp_accel_storage_t  g_accel_storage;
static bsp_led_t            g_status_led;
static app_coordinator_t    g_app;

int main(void)
{
    const board_t *board = board_init();
    if (board == 0) {
        /* Плата не піднялася. Крутити цикл нема сенсу: чекаємо на
         * сторожовий таймер, який перезапустить пристрій. */
        for (;;) {
            hal_cpu_sleep();
        }
    }

    event_queue_init(&g_events, g_event_storage, SYS_EVENT_QUEUE_CAPACITY);
    board_bind_event_queue(&g_events);

    bsp_led_init(&g_status_led, &board->led_status);

    bsp_bme280_t *env = bsp_bme280_init(&g_env_storage, board->env_bus,
                                        SYS_I2C_ADDR_BME280);
    bsp_accel_t *accel = bsp_accel_create(&g_accel_storage, board->accel_bus,
                                          SYS_I2C_ADDR_ADXL345,
                                          BSP_ACCEL_RANGE_16G);

    if (env == 0) {
        /* Без давача мікроклімату логер не має що записувати. Світимо
         * рівно й чекаємо на обслугу — тихо працювати «наполовину» гірше,
         * ніж не працювати помітно. */
        bsp_led_set_mode(&g_status_led, BSP_LED_ON);
        for (;;) {
            hal_cpu_sleep();
        }
    }

    const app_coordinator_config_t cfg = {
        .env                 = env,
        .accel               = accel, /* NULL припустимий: логер працює без вібрації */
        .led                 = &g_status_led,
        .queue               = &g_events,
        .temp_limit_c        = SYS_TEMP_LIMIT_C,
        .temp_hysteresis_c   = SYS_TEMP_HYSTERESIS_C,
        .vibration_limit_g   = SYS_VIBRATION_LIMIT_G,
        .telemetry_window_ms = SYS_TELEMETRY_WINDOW_MS,
        .fault_limit         = SYS_SENSOR_FAULT_LIMIT,
        .report              = board->report_record,
        .report_ctx          = board->report_ctx,
    };
    app_coordinator_init(&g_app, &cfg, hal_time_now_ms());

    for (;;) {
        sys_event_t evt;

        /* Вибираємо чергу до дна: обробка однієї події часто породжує
         * наступну (вимір → аварія), і засинати з непорожньою чергою
         * означало б відкласти тривогу до наступного тіку. */
        while (event_queue_pop(&g_events, &evt)) {
            app_coordinator_dispatch(&g_app, &evt);
        }

        hal_cpu_sleep();
    }
}
