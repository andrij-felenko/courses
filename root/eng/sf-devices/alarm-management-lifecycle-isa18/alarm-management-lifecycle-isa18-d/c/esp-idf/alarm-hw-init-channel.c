#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

#define MAX_ALARM_CHANNELS      32U
#define EVENT_QUEUE_CAPACITY    64U

typedef enum {
    ALARM_STATE_NORMAL = 0,
    ALARM_STATE_UNACK,
    ALARM_STATE_ACK,
    ALARM_STATE_RTN_UNACK,
    ALARM_STATE_SUPPRESSED,
    ALARM_STATE_OOS
} alarm_state_t;

typedef struct {
    uint32_t channel_id;
    alarm_state_t new_state;
    uint64_t timestamp_us;
    float raw_value;
} alarm_event_t;

typedef struct {
    float threshold_high;
    float deadband;
    uint16_t on_delay_ticks;
    uint16_t off_delay_ticks;
    uint16_t on_counter;
    uint16_t off_counter;
    alarm_state_t current_state;
    bool raw_exceeded;
} alarm_channel_cfg_t;

/* Блок глобальних атомарних прапорів для обміну між ISR та RTOS */
static _Atomic uint32_t g_active_alarms_bitmask = 0;
static alarm_channel_cfg_t g_channels[MAX_ALARM_CHANNELS];
static QueueHandle_t g_alarm_event_queue = NULL;
static TaskHandle_t g_alarm_task_handle = NULL;

/* Ініціалізація каналу тривоги */
void alarm_hw_init_channel(uint32_t id, float threshold, float deadband, uint16_t on_delay, uint16_t off_delay) {
    if (id >= MAX_ALARM_CHANNELS) return;
    g_channels[id].threshold_high = threshold;
    g_channels[id].deadband = deadband;
    g_channels[id].on_delay_ticks = on_delay;
    g_channels[id].off_delay_ticks = off_delay;
    g_channels[id].on_counter = 0;
    g_channels[id].off_counter = 0;
    g_channels[id].current_state = ALARM_STATE_NORMAL;
    g_channels[id].raw_exceeded = false;
}

/* Переривання DMA ADC: швидка оцінка та відправка подій */
void IRAM_ATTR dma_adc_isr_handler(const float *adc_samples, uint32_t count, uint64_t now_us) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    for (uint32_t i = 0; i < count && i < MAX_ALARM_CHANNELS; i++) {
        alarm_channel_cfg_t *ch = &g_channels[i];
        if (ch->current_state == ALARM_STATE_OOS || ch->current_state == ALARM_STATE_SUPPRESSED) {
            continue;
        }

        float val = adc_samples[i];
        bool high_cond = (val >= ch->threshold_high);
        bool low_cond = (val < (ch->threshold_high - ch->deadband));

        if (high_cond) {
            ch->off_counter = 0;
            if (ch->on_counter < ch->on_delay_ticks) {
                ch->on_counter++;
            }
        } else if (low_cond) {
            ch->on_counter = 0;
            if (ch->off_counter < ch->off_delay_ticks) {
                ch->off_counter++;
            }
        }

        bool triggered = (ch->on_counter >= ch->on_delay_ticks);
        bool cleared = (ch->off_counter >= ch->off_delay_ticks);

        if (triggered && !ch->raw_exceeded) {
            ch->raw_exceeded = true;
            atomic_fetch_or_explicit(&g_active_alarms_bitmask, (1U << i), memory_order_relaxed);
            
            alarm_event_t evt = {
                .channel_id = i,
                .new_state = ALARM_STATE_UNACK,
                .timestamp_us = now_us,
                .raw_value = val
            };
            xQueueSendFromISR(g_alarm_event_queue, &evt, &xHigherPriorityTaskWoken);
        } else if (cleared && ch->raw_exceeded) {
            ch->raw_exceeded = false;
            atomic_fetch_and_explicit(&g_active_alarms_bitmask, ~(1U << i), memory_order_relaxed);
            
            alarm_event_t evt = {
                .channel_id = i,
                .new_state = (ch->current_state == ALARM_STATE_ACK) ? ALARM_STATE_NORMAL : ALARM_STATE_RTN_UNACK,
                .timestamp_us = now_us,
                .raw_value = val
            };
            xQueueSendFromISR(g_alarm_event_queue, &evt, &xHigherPriorityTaskWoken);
        }
    }

    if (xHigherPriorityTaskWoken == pdTRUE) {
        portYIELD_FROM_ISR();
    }
}

/* Задача RTOS: обробка автомата станів ISA-18.2 */
void alarm_processing_task(void *pvParameters) {
    alarm_event_t evt;
    while (1) {
        if (xQueueReceive(g_alarm_event_queue, &evt, portMAX_DELAY) == pdTRUE) {
            if (evt.channel_id < MAX_ALARM_CHANNELS) {
                alarm_channel_cfg_t *ch = &g_channels[evt.channel_id];
                ch->current_state = evt.new_state;
                /* Далі виконується виклик обробників логіки безпеки */
            }
        }
    }
}
