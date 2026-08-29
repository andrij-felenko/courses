/*
 * Розділення роботи між двома пріоритетами RTOS.
 *
 * Task_Sensor крутиться на 100 Гц і не має права ні на мілісекунду затримки:
 * усе, що він робить, — O(1) арифметика й запис у чергу без блокування.
 * Task_Comms спить на порожній черзі й прокидається лише тоді, коли є що
 * везти; будити радіо з високопріоритетної задачі означало б з'їсти вікно
 * наступної вибірки на очікуванні ACK у сотні мілісекунд.
 */
#include "rtos_tasks.h"

#include <math.h>

#include "FreeRTOS.h"
#include "queue.h"
#include "task.h"

#include "edge_detector.h"
#include "telemetry_frame.h"

#define SENSOR_PERIOD_MS      10u    /* 100 Гц */
#define ADC_TIMEOUT_MS        5u
#define QUEUE_LENGTH          8u
#define ACK_TIMEOUT_MS        2000u
#define TX_ATTEMPTS           3u
#define SENSOR_STACK_WORDS    256u
#define COMMS_STACK_WORDS     512u
#define SENSOR_PRIORITY       (configMAX_PRIORITIES - 2u)
#define COMMS_PRIORITY        (tskIDLE_PRIORITY + 1u)

/* Одне повідомлення черги: звіт плюс уже розгорнута передісторія.
   Розгортаємо кільце в задачі-джерелі, бо детектор належить їй одній —
   так Task_Comms не потребує ні м'ютекса, ні доступу до стану детектора. */
typedef struct {
    telemetry_report_t report;
    float              snapshot[RING_BUFFER_CAPACITY];
    uint32_t           snapshot_len;
} telemetry_message_t;

static edge_detector_t   g_detector;
static QueueHandle_t     g_queue;

static StaticQueue_t     g_queue_control;
static uint8_t           g_queue_storage[QUEUE_LENGTH * sizeof(telemetry_message_t)];

static StaticTask_t      g_sensor_tcb;
static StackType_t       g_sensor_stack[SENSOR_STACK_WORDS];
static StaticTask_t      g_comms_tcb;
static StackType_t       g_comms_stack[COMMS_STACK_WORDS];

static volatile uint32_t g_dropped;
static volatile uint32_t g_failed_tx;

uint32_t telemetry_dropped_reports(void)      { return g_dropped; }
uint32_t telemetry_failed_transmissions(void) { return g_failed_tx; }

static void task_sensor(void *arg)
{
    (void)arg;

    TickType_t last_wake = xTaskGetTickCount();
    edge_detector_init(&g_detector, (uint32_t)(last_wake * portTICK_PERIOD_MS));

    for (;;) {
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(SENSOR_PERIOD_MS));

        const uint32_t now_ms = (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);

        float sample = 0.0f;
        if (!adc_read_sample(&sample, ADC_TIMEOUT_MS)) {
            /* Пропущене перетворення — не привід зупиняти цикл. Але й тиші
               бути не повинно: підсовуємо детектору NaN, і той оформить
               відмову давача звичайним шляхом, через аварійний звіт. */
            sample = NAN;
        }

        const telemetry_report_t report = edge_detector_process(&g_detector, sample, now_ms);
        if (report.action == DECISION_DISCARD) {
            continue;                       /* найчастіша гілка: назад у сон */
        }

        telemetry_message_t msg;
        msg.report       = report;
        msg.snapshot_len = edge_detector_snapshot(&g_detector, msg.snapshot,
                                                  RING_BUFFER_CAPACITY);

        /* Нуль замість очікування: високопріоритетна задача НЕ блокується на
           черзі. Якщо радіо не встигає — втрачаємо звіт і рахуємо втрату,
           але темп опитування давача не зриваємо. */
        if (xQueueSendToBack(g_queue, &msg, 0) != pdPASS) {
            g_dropped++;
        }
    }
}

static void task_comms(void *arg)
{
    (void)arg;

    static uint8_t frame[TELEMETRY_FRAME_MAX_SIZE];   /* не на стеку: 88 байт там зайві */
    telemetry_message_t msg;

    for (;;) {
        if (xQueueReceive(g_queue, &msg, portMAX_DELAY) != pdPASS) {
            continue;
        }

        const size_t len = telemetry_frame_encode(&msg.report,
                                                  msg.snapshot,
                                                  msg.snapshot_len,
                                                  frame,
                                                  sizeof(frame));
        if (len == 0u) {
            g_failed_tx++;
            continue;
        }

        radio_wake();

        bool acked = false;
        for (uint32_t attempt = 0; attempt < TX_ATTEMPTS && !acked; ++attempt) {
            if (radio_send(frame, len)) {
                acked = radio_wait_ack(ACK_TIMEOUT_MS);
            }
        }
        if (!acked) {
            g_failed_tx++;
        }

        /* Живлення радіокаскаду вимикаємо в БУДЬ-ЯКОМУ разі. Забутий у
           передавальному режимі PA з'їдає батарею за години. */
        radio_sleep();
    }
}

bool telemetry_start(void)
{
    g_queue = xQueueCreateStatic(QUEUE_LENGTH,
                                 sizeof(telemetry_message_t),
                                 g_queue_storage,
                                 &g_queue_control);
    if (g_queue == NULL) {
        return false;
    }

    const TaskHandle_t sensor = xTaskCreateStatic(task_sensor, "sensor",
                                                  SENSOR_STACK_WORDS, NULL,
                                                  SENSOR_PRIORITY,
                                                  g_sensor_stack, &g_sensor_tcb);
    const TaskHandle_t comms  = xTaskCreateStatic(task_comms, "comms",
                                                  COMMS_STACK_WORDS, NULL,
                                                  COMMS_PRIORITY,
                                                  g_comms_stack, &g_comms_tcb);
    return (sensor != NULL) && (comms != NULL);
}
