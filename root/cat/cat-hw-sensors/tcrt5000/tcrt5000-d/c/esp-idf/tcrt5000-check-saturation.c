#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_adc/adc_oneshot.h"
#include "driver/gpio.h"

#define TCRT_ADC_CHANNEL    ADC_CHANNEL_6 // GPIO34
#define TCRT_LED_GPIO       GPIO_NUM_25    // Керування ІЧ-світлодіодом

// Структура параметрів калібрування давача
typedef struct {
    int val_white;       // АЦП відгук над білою поверхнею (мінімальна напруга)
    int val_black;       // АЦП відгук над чорною лінією (максимальна напруга)
    int threshold;       // Обчислена порогова напруга
    bool is_saturated;   // Прапорець оптичного засвічення
} tcrt5000_calib_t;

static adc_oneshot_unit_handle_t adc_handle;

// Перевірка рівня фонового засвічення при вимкненому світлодіоді
bool tcrt5000_check_saturation(int *bg_raw) {
    gpio_set_level(TCRT_LED_GPIO, 0); // Вимикаємо ІЧ-світлодіод
    vTaskDelay(pdMS_TO_TICKS(2));
    
    adc_oneshot_read(adc_handle, TCRT_ADC_CHANNEL, bg_raw);
    // Якщо напруга на колекторі впала нижче 20% VCC (АЦП < 800 для 12-біт) при OFF LED,
    // фототранзистор відкритий фоновим інфрачервоним світлом
    if (*bg_raw < 800) {
        return true; // Виявлено оптичне засвічення (насичення)
    }
    return false;
}

// Процедура автокалібрування порогу розпізнавання
void tcrt5000_calibrate(tcrt5000_calib_t *calib, uint16_t samples) {
    int min_val = 4095;
    int max_val = 0;
    int raw_val = 0;

    gpio_set_level(TCRT_LED_GPIO, 1); // Вмикаємо ІЧ-світлодіод
    vTaskDelay(pdMS_TO_TICKS(5));

    for (uint16_t i = 0; i < samples; i++) {
        adc_oneshot_read(adc_handle, TCRT_ADC_CHANNEL, &raw_val);
        if (raw_val < min_val) min_val = raw_val; // Пошук відклику білого
        if (raw_val > max_val) max_val = raw_val; // Пошук відклику чорного
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    calib->val_white = min_val;
    calib->val_black = max_val;
    // Обчислення динамічного порогу посередині діапазону
    calib->threshold = min_val + (max_val - min_val) / 2;
}
