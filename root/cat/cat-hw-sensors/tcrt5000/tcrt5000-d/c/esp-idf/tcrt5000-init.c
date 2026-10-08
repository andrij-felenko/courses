#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_adc/adc_oneshot.h"
#include "driver/gpio.h"

#define TCRT_ADC_CHANNEL    ADC_CHANNEL_6 // GPIO34 на ESP32
#define TCRT_LED_GPIO       GPIO_NUM_25    // Гейт керування ІЧ-світлодіодом

static adc_oneshot_unit_handle_t adc1_handle;

void tcrt5000_init(void) {
    // Налаштування GPIO для керування живленням світлодіода (імпульсний режим)
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << TCRT_LED_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    // Конфігурація аналогово-цифрового перетворювача (АЦП1)
    adc_oneshot_unit_init_cfg_t init_config1 = {
        .unit_id = ADC_UNIT_1,
    };
    adc_oneshot_new_unit(&init_config1, &adc1_handle);

    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,
        .atten = ADC_ATTEN_DB_12, // Вхідний діапазон 0 - 3.3 В
    };
    adc_oneshot_config_channel(adc1_handle, TCRT_ADC_CHANNEL, &config);
}

// Зчитування з приглушенням фонового засвічення (диференціальний метод)
int tcrt5000_read_differential(void) {
    int val_off = 0, val_on = 0;
    
    // 1. Вимірювання фону при вимкненому світлодіоді
    gpio_set_level(TCRT_LED_GPIO, 0);
    vTaskDelay(pdMS_TO_TICKS(1));
    adc_oneshot_read(adc1_handle, TCRT_ADC_CHANNEL, &val_off);
    
    // 2. Вимірювання сигналу при увімкненому світлодіоді
    gpio_set_level(TCRT_LED_GPIO, 1);
    esp_rom_delay_us(50); // Пауза для виходу світлодіода на режим
    adc_oneshot_read(adc1_handle, TCRT_ADC_CHANNEL, &val_on);
    
    gpio_set_level(TCRT_LED_GPIO, 0);
    
    // Оскільки при відбиванні напруга падає, корисний сигнал це різниця val_off - val_on
    int signal = val_off - val_on;
    return (signal < 0) ? 0 : signal;
}
