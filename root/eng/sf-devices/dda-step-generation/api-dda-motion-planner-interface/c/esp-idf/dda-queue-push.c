#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include "driver/gptimer.h"
#include "driver/gpio.h"

#define DDA_MAX_AXES 3
#define DDA_RING_BUFFER_SIZE 16

typedef struct {
    uint32_t total_steps;
    uint32_t dir_mask;
    uint32_t axis_delta[DDA_MAX_AXES];
    uint32_t initial_period_ticks;
    int32_t timer_acc_inc;
} dda_segment_t;

typedef struct {
    dda_segment_t buffer[DDA_RING_BUFFER_SIZE];
    atomic_size_t head;
    atomic_size_t tail;
} dda_ring_buffer_t;

static dda_ring_buffer_t g_dda_queue = { .head = 0, .tail = 0 };
static uint32_t g_dda_acc[DDA_MAX_AXES];
static uint32_t g_current_step_count = 0;
static uint32_t g_current_period = 0;
static bool g_is_busy = false;

// Атомарне додавання сегмента у кільцевий буфер з фонового потоку
bool dda_queue_push(const dda_segment_t *seg) {
    size_t h = atomic_load_explicit(&g_dda_queue.head, memory_order_relaxed);
    size_t t = atomic_load_explicit(&g_dda_queue.tail, memory_order_acquire);
    size_t next_h = (h + 1) % DDA_RING_BUFFER_SIZE;
    
    if (next_h == t) {
        return false; // Буфер переповнений
    }
    
    g_dda_queue.buffer[h] = *seg;
    atomic_store_explicit(&g_dda_queue.head, next_h, memory_order_release);
    return true;
}

// ISR апаратного таймера генерації кроків
static bool IRAM_ATTR dda_timer_isr_callback(gptimer_handle_t timer, const gptimer_alarm_event_data_t *edata, void *user_ctx) {
    size_t t = atomic_load_explicit(&g_dda_queue.tail, memory_order_relaxed);
    size_t h = atomic_load_explicit(&g_dda_queue.head, memory_order_acquire);
    
    if (t == h) {
        g_is_busy = false;
        gptimer_stop(timer);
        return false; // Буфер порожній, зупиняємо таймер
    }
    
    dda_segment_t *cur = &g_dda_queue.buffer[t];
    
    if (g_current_step_count == 0) {
        // Ініціалізація нового сегмента руху
        g_current_period = cur->initial_period_ticks;
        for (int i = 0; i < DDA_MAX_AXES; i++) {
            g_dda_acc[i] = cur->total_steps >> 1;
        }
        // Встановлення сигналів напрямку GPIO
        gpio_set_level(GPIO_NUM_18, (cur->dir_mask & 0x01) ? 1 : 0);
    }
    
    // Формування фронту імпульсу STEP для провідної осі
    gpio_set_level(GPIO_NUM_19, 1);
    
    // Інкрементне оновлення DDA-акумуляторів ведених осей
    for (int i = 1; i < DDA_MAX_AXES; i++) {
        g_dda_acc[i] += cur->axis_delta[i];
        if (g_dda_acc[i] >= cur->total_steps) {
            g_dda_acc[i] -= cur->total_steps;
            gpio_set_level(GPIO_NUM_21 + i, 1);
        }
    }
    
    // Скидання імпульсів STEP (формування спаду)
    gpio_set_level(GPIO_NUM_19, 0);
    for (int i = 1; i < DDA_MAX_AXES; i++) {
        gpio_set_level(GPIO_NUM_21 + i, 0);
    }
    
    g_current_step_count++;
    g_current_period += cur->timer_acc_inc;
    
    // Оновлення регістру тривоги таймера
    gptimer_alarm_config_t alarm_cfg = {
        .alarm_count = edata->alarm_value + g_current_period,
    };
    gptimer_set_alarm_action(timer, &alarm_cfg);
    
    if (g_current_step_count >= cur->total_steps) {
        g_current_step_count = 0;
        size_t next_t = (t + 1) % DDA_RING_BUFFER_SIZE;
        atomic_store_explicit(&g_dda_queue.tail, next_t, memory_order_release);
    }
    
    return true;
}
