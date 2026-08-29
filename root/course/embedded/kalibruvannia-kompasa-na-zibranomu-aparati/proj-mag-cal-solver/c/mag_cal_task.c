/* ==========================================================================
 *  mag_cal_task.c — інтеграція конвеєра у FreeRTOS
 *
 *  Два завдання з різними пріоритетами:
 *    · сенсорне (100 Гц, високий пріоритет) — читає магнітометр і гіроскоп,
 *      коригує вимір чинними коефіцієнтами й віддає його оцінювачу; виклик
 *      накопичувача займає одиниці мікросекунд;
 *    · калібрувальне (10 Гц, низький пріоритет) — тайм-аути, телеметрія і
 *      сам розв'язувач, який рахує 2–4 мс і тому не має права виконуватись
 *      під час, украдений у контуру стабілізації.
 *
 *  Спільні дані — накопичувач і чинні коефіцієнти — накриті м'ютексом.
 *  Розв'язувач працює НЕ під ним: він отримує копію хмари, зняту за десяток
 *  мікросекунд, і далі мовчки рахує свою математику.
 * ========================================================================== */

#include <stdbool.h>
#include <stdint.h>

#include "FreeRTOS.h"
#include "semphr.h"
#include "task.h"

#include "mag_cal_fsm.h"
#include "mag_cal_solver.h"

/* --- Порт плати: драйвери й годинник --- */
uint32_t board_millis(void);
bool     board_mag_read(vec3_t *out_ut);        /* сирі мкТл із RM3100 / IST8310 */
bool     board_gyro_read(vec3_t *out_rad_s);
void     board_mag_publish(vec3_t calibrated);  /* вхід оцінювача положення */

/* --- Параметри завдань --- */
#define MAG_CAL_SENSOR_PERIOD_MS  10u    /* 100 Гц */
#define MAG_CAL_WORKER_PERIOD_MS  100u   /* 10 Гц */
#define MAG_CAL_SENSOR_PRIORITY   (configMAX_PRIORITIES - 2)
#define MAG_CAL_WORKER_PRIORITY   (tskIDLE_PRIORITY + 1)
#define MAG_CAL_SENSOR_STACK      512u   /* слів, не байтів */
#define MAG_CAL_WORKER_STACK      1024u  /* розв'язувачу потрібні H[9][9] на стеку */

/* Уся пам'ять статична: динамічного розподілу в польотному контурі немає */
static StaticTask_t      s_sensor_tcb;
static StackType_t       s_sensor_stack[MAG_CAL_SENSOR_STACK];
static StaticTask_t      s_worker_tcb;
static StackType_t       s_worker_stack[MAG_CAL_WORKER_STACK];
static StaticSemaphore_t s_mutex_storage;
static SemaphoreHandle_t s_mutex;

static mag_cal_fsm_t        s_fsm;
static mag_cal_collector_t  s_snapshot;   /* ~3.5 КБ; живе лише у робочому завданні */

/* Заявки з обробника команд MAVLink (MAV_CMD_DO_START_MAG_CAL і скасування).
 * Прапорці, а не пряме втручання: команда приходить із чужого потоку. */
static volatile bool s_start_requested;
static volatile bool s_cancel_requested;

void mag_cal_request_start(void)  { s_start_requested  = true; }
void mag_cal_request_cancel(void) { s_cancel_requested = true; }

/* Знімок стану для гейта озброєння — теж під м'ютексом */
bool mag_cal_arming_allowed_safe(void) {
    bool allowed = false;
    if (xSemaphoreTake(s_mutex, pdMS_TO_TICKS(5)) == pdTRUE) {
        allowed = mag_cal_fsm_arming_allowed(&s_fsm);
        xSemaphoreGive(s_mutex);
    }
    return allowed;   /* м'ютекс зайнятий довше за 5 мс — не озброюємось */
}

static void mag_cal_sensor_task(void *arg) {
    (void)arg;
    TickType_t last_wake = xTaskGetTickCount();

    for (;;) {
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(MAG_CAL_SENSOR_PERIOD_MS));

        vec3_t raw, gyro;
        if (!board_mag_read(&raw) || !board_gyro_read(&gyro)) {
            continue;               /* збій шини: пропускаємо такт мовчки */
        }

        const uint32_t now = board_millis();

        /* Тримаємо м'ютекс рівно стільки, скільки треба на копіювання
         * коефіцієнтів і запис однієї точки в комірку. */
        vec3_t calibrated = raw;
        if (xSemaphoreTake(s_mutex, pdMS_TO_TICKS(2)) == pdTRUE) {
            calibrated = mag_cal_fsm_correct(&s_fsm, raw);
            (void)mag_cal_fsm_push(&s_fsm, raw, gyro, now);
            xSemaphoreGive(s_mutex);
        }

        board_mag_publish(calibrated);
    }
}

static void mag_cal_worker_task(void *arg) {
    (void)arg;
    TickType_t last_wake = xTaskGetTickCount();

    /* Старт плати: піднімаємо коефіцієнти з Flash і звіряємо CRC32 */
    if (xSemaphoreTake(s_mutex, portMAX_DELAY) == pdTRUE) {
        (void)mag_cal_fsm_boot(&s_fsm, board_millis());
        xSemaphoreGive(s_mutex);
    }

    for (;;) {
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(MAG_CAL_WORKER_PERIOD_MS));

        const uint32_t now = board_millis();
        bool need_solve = false;

        if (xSemaphoreTake(s_mutex, portMAX_DELAY) != pdTRUE) {
            continue;
        }

        if (s_start_requested) {
            s_start_requested = false;
            (void)mag_cal_fsm_start(&s_fsm, now);
        }
        if (s_cancel_requested) {
            s_cancel_requested = false;
            mag_cal_fsm_cancel(&s_fsm, now);
        }

        mag_cal_fsm_service(&s_fsm, now);

        if (mag_cal_fsm_ready_to_solve(&s_fsm)) {
            mag_cal_fsm_begin_solve(&s_fsm, now);
            mag_cal_collector_snapshot(&s_fsm.collector, &s_snapshot);
            need_solve = true;
        }
        xSemaphoreGive(s_mutex);

        if (!need_solve) {
            continue;
        }

        /* Найдорожча частина циклу — і вона поза м'ютексом */
        mag_cal_result_t result;
        const mag_cal_solve_status_t status = mag_cal_run_solver(&s_snapshot, &result);

        if (xSemaphoreTake(s_mutex, portMAX_DELAY) == pdTRUE) {
            mag_cal_fsm_submit(&s_fsm, status, &result, board_millis());
            xSemaphoreGive(s_mutex);
        }
    }
}

void mag_cal_task_start(uint8_t compass_id, uint8_t system_id,
                        uint8_t component_id, float earth_field_ut) {
    s_mutex = xSemaphoreCreateMutexStatic(&s_mutex_storage);
    configASSERT(s_mutex != NULL);

    mag_cal_fsm_init(&s_fsm, compass_id, system_id, component_id, earth_field_ut);

    (void)xTaskCreateStatic(mag_cal_sensor_task, "mag_sensor",
                            MAG_CAL_SENSOR_STACK, NULL,
                            MAG_CAL_SENSOR_PRIORITY,
                            s_sensor_stack, &s_sensor_tcb);

    (void)xTaskCreateStatic(mag_cal_worker_task, "mag_cal",
                            MAG_CAL_WORKER_STACK, NULL,
                            MAG_CAL_WORKER_PRIORITY,
                            s_worker_stack, &s_worker_tcb);
}
