#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include "realtime_ml_controller.h"

static rt_triple_buffer_t g_tb;
static rt_ml_controller_t g_ctrl;
static rt_fallback_pid_t g_pid;
static atomic_bool g_running = true;

static uint64_t get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000ULL + (uint64_t)ts.tv_nsec / 1000ULL;
}

void* producer_ml_thread(void *arg) {
    (void)arg;
    uint32_t frame_id = 0;

    while (atomic_load_explicit(&g_running, memory_order_relaxed)) {
        /* Емуляція інференсу нейромережі: базова затримка 30 мс + випадковий джиттер */
        uint32_t sleep_ms = 30 + (rand() % 15);
        
        /* Штучна інжекція пропуску дедлайну кожні 20 кадрів */
        if (frame_id % 20 == 0) {
            sleep_ms += 75; /* Затримка перевищує дедлайн 40 мс */
        }

        usleep(sleep_ms * 1000);

        rt_ml_frame_t frame;
        frame.frame_id = ++frame_id;
        frame.timestamp_us = get_time_us();
        frame.confidence = 0.95f;
        
        /* Генерація тестового гармонічного сигналу поправки */
        float t_sec = (float)frame.timestamp_us * 1e-6f;
        for (int i = 0; i < RT_ML_MAX_DIM; ++i) {
            frame.values[i] = sinf(t_sec * 2.0f + (float)i * 0.5f) * 10.0f;
        }

        rt_triple_buffer_write(&g_tb, &frame);
    }
    return NULL;
}

void* consumer_control_thread(void *arg) {
    (void)arg;
    uint64_t next_tick_us = get_time_us();
    uint32_t total_ticks = 0;
    uint32_t fresh_ticks = 0;
    uint32_t extrap_ticks = 0;
    uint32_t fallback_ticks = 0;

    while (total_ticks < 5000) {
        uint64_t now_us = get_time_us();
        rt_ml_frame_t frame;
        bool is_fresh = rt_triple_buffer_read(&g_tb, &frame);

        float correction[RT_ML_MAX_DIM];
        rt_ml_status_t status = rt_ml_controller_update(&g_ctrl, &frame, is_fresh, now_us, correction);

        /* Фізичний модельний контур */
        float setpoint = 50.0f;
        static float plant_state = 0.0f;
        
        bool is_fallback = (status == RT_ML_STATUS_FALLBACK_PID || status == RT_ML_STATUS_EMERGENCY_STOP);
        float external_u = 1.2f * (setpoint - plant_state) + correction[0];
        
        float applied_u = rt_fallback_pid_step(&g_pid, setpoint, plant_state, external_u, is_fallback);
        
        /* Динаміка об'єкта 1-го порядку */
        plant_state += (applied_u - plant_state) * 0.02f;

        switch (status) {
            case RT_ML_STATUS_FRESH: fresh_ticks++; break;
            case RT_ML_STATUS_EXTRAPOLATED: extrap_ticks++; break;
            case RT_ML_STATUS_FALLBACK_PID: fallback_ticks++; break;
            default: break;
        }

        total_ticks++;
        next_tick_us += 2000; /* 500 Гц контур (2 мс) */
        
        int64_t sleep_remain = (int64_t)next_tick_us - (int64_t)get_time_us();
        if (sleep_remain > 0) {
            usleep((useconds_t)sleep_remain);
        }
    }

    printf("=== РЕЗУЛЬТАТИ СТРЕС-ТЕСТУ КОНТУРУ КЕРУВАННЯ (5000 тактів) ===\n");
    printf("Тактів зі свіжим виводом:   %u (%.1f%%)\n", fresh_ticks, (float)fresh_ticks / 50.0f);
    printf("Тактів з екстраполяцією:    %u (%.1f%%)\n", extrap_ticks, (float)extrap_ticks / 50.0f);
    printf("Тактів у режимі Fallback:   %u (%.1f%%)\n", fallback_ticks, (float)fallback_ticks / 50.0f);
    printf("Всього пропусків дедлайну:  %u\n", g_ctrl.deadline_miss_count);
    printf("Максимальна латентність:    %.2f мс\n", (float)g_ctrl.max_observed_latency_us * 0.001f);

    return NULL;
}

int main(void) {
    rt_triple_buffer_init(&g_tb);

    rt_watchdog_config_t cfg = {
        .deadline_limit_us = 45000,
        .max_extrap_us = 100000,
        .fatal_timeout_us = 500000,
        .decay_lambda = 15.0f,
        .max_slew_rate = 100.0f
    };
    rt_ml_controller_init(&g_ctrl, &cfg);
    rt_fallback_pid_init(&g_pid, 2.5f, 0.8f, 0.15f, 0.002f, -100.0f, 100.0f);

    pthread_t prod, cons;
    pthread_create(&prod, NULL, producer_ml_thread, NULL);
    pthread_create(&cons, NULL, consumer_control_thread, NULL);

    pthread_join(cons, NULL);
    atomic_store_explicit(&g_running, false, memory_order_relaxed);
    pthread_join(prod, NULL);

    return 0;
}
