#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <math.h>

#define BUFFER_SIZE 256
#define FILTER_WINDOW 5

// Структура для зберігання параметрів вимірювань
typedef struct {
    uint32_t timestamp_ms;
    float pressure_upstream;
    float pressure_downstream;
    float optical_gate;
} Sample_t;

// Проста структура ковзного фільтра для згладжування шумів АЦП
typedef struct {
    float buffer[FILTER_WINDOW];
    uint8_t index;
    uint8_t count;
} MovingAverageFilter_t;

void filter_init(MovingAverageFilter_t *f) {
    f->index = 0;
    f->count = 0;
    for (int i = 0; i < FILTER_WINDOW; i++) {
        f->buffer[i] = 0.0f;
    }
}

float filter_update(MovingAverageFilter_t *f, float input) {
    f->buffer[f->index] = input;
    f->index = (f->index + 1) % FILTER_WINDOW;
    if (f->count < FILTER_WINDOW) {
        f->count++;
    }

    float sum = 0.0f;
    for (uint8_t i = 0; i < f->count; i++) {
        sum += f->buffer[i];
    }
    return sum / f->count;
}

// Функція пошуку переходу перепаду тиску через нуль (зміна знака dp = P_up - P_down)
bool detect_zero_crossing(float prev_dp, float curr_dp, uint32_t *crossing_time, uint32_t t) {
    if ((prev_dp < 0.0f && curr_dp >= 0.0f) || (prev_dp > 0.0f && curr_dp <= 0.0f)) {
        *crossing_time = t;
        return true;
    }
    return false;
}

int main(void) {
    printf("=== Microfluidic Reed Valve Dynamic Analysis (C) ===\n");

    // Імітація буфера даних від датчиків (наприклад, із мікроконтролерного АЦП)
    // У реальній системі дані надходють із DMA-буферів кільцевої пам'яті
    Sample_t raw_data[BUFFER_SIZE];
    
    // Ініціалізація фільтрів для кожного каналу
    MovingAverageFilter_t filter_up, filter_down, filter_opt;
    filter_init(&filter_up);
    filter_init(&filter_down);
    filter_init(&filter_opt);

    // Генерація синтетичного тестового сигналу для демонстрації роботи алгоритму
    for (int i = 0; i < BUFFER_SIZE; i++) {
        raw_data[i].timestamp_ms = i * 2; // дискретизація кожні 2 мс
        // Синусоїдальний тиск із шумом
        float t_sec = i * 0.002f;
        raw_data[i].pressure_upstream = 50.0f * sinf(2.0f * 3.14159f * 10.0f * t_sec);
        raw_data[i].pressure_downstream = 45.0f * sinf(2.0f * 3.14159f * 10.0f * t_sec - 0.2f);
        
        // Оптичний датчик затвора: спрацьовує (переходить у 1.0), коли потік змінює напрямок
        if (t_sec > 0.05f && t_sec < 0.15f) {
            raw_data[i].optical_gate = 1.0f;
        } else {
            raw_data[i].optical_gate = 0.0f;
        }
    }

    float prev_dp = 0.0f;
    uint32_t zero_crossing_time = 0;
    bool zero_crossing_found = false;
    uint32_t valve_closure_time = 0;
    bool valve_closed = false;

    printf("Processing %d samples...\n", BUFFER_SIZE);

    for (int i = 0; i < BUFFER_SIZE; i++) {
        // Застосування цифрової фільтрації
        float p_up_filtered = filter_update(&filter_up, raw_data[i].pressure_upstream);
        float p_down_filtered = filter_update(&filter_down, raw_data[i].pressure_downstream);
        float opt_filtered = filter_update(&filter_opt, raw_data[i].optical_gate);

        // Обчислення перепаду тиску на клапані
        float curr_dp = p_up_filtered - p_down_filtered;

        // Пошук моменту зміни знака перепаду тиску (нуль-перехід)
        if (i > 0) {
            uint32_t t_zc = 0;
            if (!zero_crossing_found && detect_zero_crossing(prev_dp, curr_dp, &t_zc, raw_data[i].timestamp_ms)) {
                zero_crossing_time = raw_data[i].timestamp_ms;
                zero_crossing_found = true;
                printf("[EVENT] Zero crossing detected at t = %u ms (dp = %.2f)\n", zero_crossing_time, curr_dp);
            }
        }

        // Фіксація закриття затвора за оптичним датчиком (перехід через поріг 0.5)
        if (!valve_closed && opt_filtered > 0.5f) {
            valve_closure_time = raw_data[i].timestamp_ms;
            valve_closed = true;
            printf("[EVENT] Valve closure detected at t = %u ms (optical gate active)\n", valve_closure_time);
        }

        prev_dp = curr_dp;
    }

    // Обчислення динамічної затримки спрацьовування
    if (zero_crossing_found && valve_closed) {
        int32_t delay_ms = (int32_t)valve_closure_time - (int32_t)zero_crossing_time;
        printf("\n[RESULT] Pressure zero crossing: %u ms\n", zero_crossing_time);
        printf("[RESULT] Valve actual closure: %u ms\n", valve_closure_time);
        printf("[RESULT] Dynamic actuation delay: %d ms\n", delay_ms);
    } else {
        printf("\n[WARNING] Could not determine complete actuation cycle (missing events).\n");
    }

    return 0;
}
