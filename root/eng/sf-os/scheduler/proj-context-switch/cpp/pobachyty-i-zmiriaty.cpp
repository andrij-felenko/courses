// --- Фрагмент 1: вартість перемикання контексту ---
#include <Arduino.h>
#include "esp_cpu.h"          // esp_cpu_get_cycle_count()

static volatile uint32_t t_before = 0;
static volatile uint32_t total_cost = 0;
static const int N = 10000;
static volatile int count = 0;

// Задача-«пінгер»: фіксує момент до yield
void taskPing(void*) {
    for (;;) {
        t_before = esp_cpu_get_cycle_count();
        taskYIELD();           // вимушене перемикання на taskPong
        // повернулися — підраховуємо вартість
        uint32_t cost = esp_cpu_get_cycle_count() - t_before;
        total_cost += cost;
        count++;
        if (count >= N) {
            uint32_t avg = total_cost / N;
            // cost_ns = avg_cycles / 240.0   (ESP32 типово 240 МГц)
            float ns = (float)avg / 240.0f;
            Serial.printf("Перемикання: ~%lu тактів = ~%.1f нс\n", avg, ns);
            total_cost = 0; count = 0;
        }
    }
}

// Задача-«понгер»: просто повертає управління
void taskPong(void*) {
    for (;;) {
        taskYIELD();
    }
}

void setup() {
    Serial.begin(115200);
    // Обидві задачі — на ядрі 1, однаковий пріоритет
    xTaskCreatePinnedToCore(taskPing, "ping", 2048, nullptr, 2, nullptr, 1);
    xTaskCreatePinnedToCore(taskPong, "pong", 2048, nullptr, 2, nullptr, 1);
}

void loop() { vTaskDelay(portMAX_DELAY); }
