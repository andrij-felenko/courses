#include <stdio.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "phase_selector.h"

static const char *TAG = "MAIN_APP";

#define SAMPLES_PER_CYCLE 64

/// Задача розрахунку та виклику алгоритму оновлення перемикача фаз
static void phase_selector_task(void *pvParameters)
{
    float buf_l1[SAMPLES_PER_CYCLE];
    float buf_l2[SAMPLES_PER_CYCLE];
    float buf_l3[SAMPLES_PER_CYCLE];

    // Імітаційні параметри амплітуд напруг для демонстрації (В)
    float sim_v_l1 = 220.0f;
    float sim_v_l2 = 225.0f;
    float sim_v_l3 = 218.0f;

    uint32_t step_counter = 0;
    phase_selector_status_t status;

    while (1) {
        step_counter++;

        // Імітація провалу напруги фази L1 на 10-й секунді для демонстрування резервування
        if (step_counter > 200 && step_counter < 500) {
            sim_v_l1 = 160.0f; // Провал нижче порогу 180 В
        } else {
            sim_v_l1 = 220.0f; // Відновлення норми 220 В
        }

        // Генерація оцифрованих синусоїдальних вибірок напруги
        for (int i = 0; i < SAMPLES_PER_CYCLE; i++) {
            float rad = (2.0f * M_PI * i) / (float)SAMPLES_PER_CYCLE;
            buf_l1[i] = sim_v_l1 * sqrtf(2.0f) * sinf(rad);
            buf_l2[i] = sim_v_l2 * sqrtf(2.0f) * sinf(rad - (2.0f * M_PI / 3.0f));
            buf_l3[i] = sim_v_l3 * sqrtf(2.0f) * sinf(rad + (2.0f * M_PI / 3.0f));
        }

        // Передача вибірок для розрахунку True-RMS
        phase_selector_process_samples(buf_l1, buf_l2, buf_l3, SAMPLES_PER_CYCLE);

        // Оновлення FSM перемикача фаз
        phase_selector_update(&status);

        // Вивід стану кожні 500 мс (кожні 10 ітерацій)
        if (step_counter % 10 == 0) {
            ESP_LOGI(TAG, "RMS: L1=%.1fV (%s), L2=%.1fV (%s), L3=%.1fV (%s) | Активна фаза: %d | FSM стан: %d",
                     status.v_rms_l1, status.is_valid_l1 ? "НОРМА" : "АВАРІЯ",
                     status.v_rms_l2, status.is_valid_l2 ? "НОРМА" : "АВАРІЯ",
                     status.v_rms_l3, status.is_valid_l3 ? "НОРМА" : "АВАРІЯ",
                     status.active_phase,
                     status.fsm_state);
        }

        // Періодичність обробки 50 мс
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "Запуск мікроконтролерного блоку автоматичного вибору фази (АВР)");

    // Налаштування конфігурації
    phase_selector_config_t config = {
        .adc_channel_l1 = ADC1_CHANNEL_0,
        .adc_channel_l2 = ADC1_CHANNEL_3,
        .adc_channel_l3 = ADC1_CHANNEL_6,
        .relay_gpio_l1  = GPIO_NUM_25,
        .relay_gpio_l2  = GPIO_NUM_26,
        .relay_gpio_l3  = GPIO_NUM_27,
        .v_min_threshold = 180.0f,  // Нижня межа 180 В
        .v_max_threshold = 250.0f,  // Верхня межа 250 В
        .v_hysteresis    = 5.0f,    // Гістерезис 5 В
        .t_transfer_ms   = 100,     // Пауза гасіння дуги dead-time 100 мс
        .t_return_ms     = 3000,    // Затримка повернення на L1 3000 мс
        .priority_phase  = PHASE_L1
    };

    esp_err_t err = phase_selector_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати перемикач фаз");
        return;
    }

    // Створення задач FreeRTOS
    xTaskCreate(phase_selector_task, "phase_selector_task", 4096, NULL, 5, NULL);
}
