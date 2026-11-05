#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/gpio.h"
#include "esp_timer.h"

// Фізичні виводи підключення
#define DIGIMATIC_REQ_PIN  GPIO_NUM_4
#define DIGIMATIC_CLK_PIN  GPIO_NUM_5
#define DIGIMATIC_DATA_PIN GPIO_NUM_6

typedef struct {
    double value_mm;
    bool is_inch;
    bool valid;
} spc_measurement_t;

static QueueHandle_t s_spc_queue = NULL;
static volatile uint64_t s_shift_reg = 0;
static volatile uint8_t s_bit_count = 0;
static volatile int64_t s_last_clk_us = 0;

// Обробник переривання по спаду CLK
static void IRAM_ATTR spc_clk_isr_handler(void* arg) {
    int64_t now_us = esp_timer_get_time();
    
    // Перевірка таймауту між кадрами (> 2.0 мс)
    if ((now_us - s_last_clk_us) > 2000) {
        s_bit_count = 0;
        s_shift_reg = 0;
    }
    s_last_clk_us = now_us;

    int data_bit = gpio_get_level(DIGIMATIC_DATA_PIN);
    
    if (s_bit_count < 52) {
        s_shift_reg |= ((uint64_t)(data_bit & 0x01) << s_bit_count);
        s_bit_count++;
        
        if (s_bit_count == 52) {
            BaseType_t xHigherPriorityTaskWoken = pdFALSE;
            vTaskNotifyGiveFromISR((TaskHandle_t)arg, &xHigherPriorityTaskWoken);
            if (xHigherPriorityTaskWoken) {
                portYIELD_FROM_ISR();
            }
        }
    }
}

// Задача обробки та декодування кадру Mitutoyo Digimatic
void digimatic_decoder_task(void* pvParameters) {
    spc_measurement_t result;
    
    while (1) {
        // Запит нового вимірювання (імпульс REQ LOW на 1 мс)
        gpio_set_level(DIGIMATIC_REQ_PIN, 0);
        vTaskDelay(pdMS_TO_TICKS(1));
        gpio_set_level(DIGIMATIC_REQ_PIN, 1);

        // Очікування завершення прийому 52 бітів
        if (ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(200)) > 0) {
            uint64_t frame = s_shift_reg;
            
            // Виділення півбайтів (13 nibbles по 4 біти)
            uint8_t d[13];
            for (int i = 0; i < 13; i++) {
                d[i] = (frame >> (i * 4)) & 0x0F;
            }

            // Валідація преамбули 0xF 0xF 0xF 0xF
            if (d[0] == 0xF && d[1] == 0xF && d[2] == 0xF && d[3] == 0xF) {
                int32_t raw = d[5] + d[6]*10 + d[7]*100 + d[8]*1000 + d[9]*10000 + d[10]*100000;
                
                double div = 1.0;
                for (int p = 0; p < d[11]; p++) div *= 10.0;
                
                result.value_mm = (double)raw / div;
                if (d[4] & 0x08) {
                    result.value_mm = -result.value_mm;
                }
                result.is_inch = (d[12] & 0x01) != 0;
                result.valid = true;

                xQueueSend(s_spc_queue, &result, 0);
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(100)); // Періодичність опитування 10 Гц
    }
}
