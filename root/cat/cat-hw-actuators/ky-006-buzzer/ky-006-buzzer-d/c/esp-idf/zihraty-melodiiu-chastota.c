#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// частоти нот у герцах
#define C4 262
#define D4 294
#define E4 330
#define F4 349
#define G4 392

// мелодія: пари {частота, тривалість у мс}. 0 = пауза (тиша)
static const struct { uint32_t freq; uint32_t ms; } melody[] = {
    {E4, 300}, {E4, 300}, {F4, 300}, {G4, 300},
    {G4, 300}, {F4, 300}, {E4, 300}, {D4, 300}, {C4, 500},
};

void play_melody(void)              // канал LEDC уже налаштовано (див. вище)
{
    for (size_t i = 0; i < sizeof melody / sizeof melody[0]; i++) {
        if (melody[i].freq > 0) {
            ledc_set_freq(LEDC_LOW_SPEED_MODE, LEDC_TIMER_0, melody[i].freq);
            ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 512);  // 50 %
        } else {
            ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);    // пауза
        }
        ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
        vTaskDelay(pdMS_TO_TICKS(melody[i].ms));

        // між нотами — маленький проміжок тиші, щоб ноти не зливались
        ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);
        ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
        vTaskDelay(pdMS_TO_TICKS(40));
    }
}
