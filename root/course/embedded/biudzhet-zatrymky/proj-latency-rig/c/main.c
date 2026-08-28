#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define LATENCY_MAX_SAMPLES 256
#define TIMEOUT_US          250000UL   // 250 мс таймаут очікування

typedef struct {
    uint32_t samples[LATENCY_MAX_SAMPLES];
    uint16_t count;
    uint16_t timeouts;
    uint32_t min_us;
    uint32_t max_us;
    uint32_t mean_us;
    uint32_t p50_us;
    uint32_t p95_us;
    uint32_t p99_us;
    uint32_t jitter_us;
} latency_stats_t;

typedef enum {
    RIG_IDLE,
    RIG_WAITING_RESPONSE,
    RIG_COOLDOWN
} rig_state_t;

static volatile rig_state_t g_rig_state = RIG_IDLE;
static volatile uint32_t g_t_start_us = 0;
static volatile uint32_t g_last_latency_us = 0;
static volatile bool g_sample_ready = false;

// Апаратні заглушки доступу до регістрів конкретного MCU
extern void hardware_led_set(bool state);
extern uint32_t hardware_timer_get_us(void);

// Обробник зовнішнього апаратного переривання від фотодіодного компаратора (EXTI ISR)
void EXTI_Optical_IRQHandler(void) {
    if (g_rig_state == RIG_WAITING_RESPONSE) {
        uint32_t t_now = hardware_timer_get_us();
        g_last_latency_us = t_now - g_t_start_us;
        g_sample_ready = true;
        g_rig_state = RIG_COOLDOWN;
        hardware_led_set(false);
    }
}

// Ініціалізація структури статистичних вимірювань
void latency_stats_init(latency_stats_t *stats) {
    memset(stats, 0, sizeof(latency_stats_t));
}

// Запуск одиничного оптичного тесту
void latency_rig_trigger(void) {
    if (g_rig_state != RIG_IDLE) return;
    
    g_sample_ready = false;
    g_rig_state = RIG_WAITING_RESPONSE;
    g_t_start_us = hardware_timer_get_us();
    hardware_led_set(true);
}

// Опитування поточного стану тесту та обробка таймаутів
bool latency_rig_poll(uint32_t *out_latency_us, bool *out_is_timeout) {
    if (g_rig_state == RIG_WAITING_RESPONSE) {
        uint32_t elapsed = hardware_timer_get_us() - g_t_start_us;
        if (elapsed >= TIMEOUT_US) {
            hardware_led_set(false);
            g_rig_state = RIG_COOLDOWN;
            *out_is_timeout = true;
            *out_latency_us = TIMEOUT_US;
            return true;
        }
    }
    
    if (g_sample_ready) {
        g_sample_ready = false;
        *out_latency_us = g_last_latency_us;
        *out_is_timeout = false;
        return true;
    }
    
    return false;
}

// Переведення стенда в режим готовності після періоду охолодження
void latency_rig_arm(void) {
    if (g_rig_state == RIG_COOLDOWN) {
        g_rig_state = RIG_IDLE;
    }
}

// Додавання успішного зразка до статистичного масиву
bool latency_stats_add_sample(latency_stats_t *stats, uint32_t latency_us, bool is_timeout) {
    if (is_timeout) {
        stats->timeouts++;
        return true;
    }
    if (stats->count >= LATENCY_MAX_SAMPLES) return false;
    stats->samples[stats->count++] = latency_us;
    return true;
}

// Сортування масиву на місці для швидкого знаходження перцентилів
static void sort_samples(uint32_t *arr, uint16_t n) {
    for (uint16_t i = 1; i < n; i++) {
        uint32_t key = arr[i];
        int32_t j = (int32_t)i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

// Розрахунок підсумкових статистичних параметрів
void latency_stats_compute(latency_stats_t *stats) {
    if (stats->count == 0) return;

    uint32_t sorted[LATENCY_MAX_SAMPLES];
    memcpy(sorted, stats->samples, stats->count * sizeof(uint32_t));
    sort_samples(sorted, stats->count);

    stats->min_us = sorted[0];
    stats->max_us = sorted[stats->count - 1];

    uint64_t sum = 0;
    for (uint16_t i = 0; i < stats->count; i++) {
        sum += sorted[i];
    }
    stats->mean_us = (uint32_t)(sum / stats->count);

    // Розрахунок медіани та перцентилів
    stats->p50_us = sorted[(stats->count * 50) / 100];
    stats->p95_us = sorted[(stats->count * 95) / 100];
    stats->p99_us = sorted[(stats->count * 99) / 100];

    // Середнє абсолютне відхилення від середнього (оцінка джитера)
    uint64_t dev_sum = 0;
    for (uint16_t i = 0; i < stats->count; i++) {
        int64_t diff = (int64_t)sorted[i] - (int64_t)stats->mean_us;
        dev_sum += (diff < 0) ? -diff : diff;
    }
    stats->jitter_us = (uint32_t)(dev_sum / stats->count);
}
