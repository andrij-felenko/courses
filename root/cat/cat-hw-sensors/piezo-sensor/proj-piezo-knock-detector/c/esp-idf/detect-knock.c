#include "driver/adc.h"
#include "esp_timer.h"

#define SENSOR_CHANNEL ADC1_CHANNEL_6
#define NOISE_THRESHOLD 150
#define DEAD_TIME_US 80000

static uint64_t last_knock_time = 0;

void detect_knock(void) {
    uint64_t now = esp_timer_get_time();
    int raw_val = adc1_get_raw(SENSOR_CHANNEL);

    if (now - last_knock_time < DEAD_TIME_US) {
        return;
    }

    if (raw_val > NOISE_THRESHOLD) {
        last_knock_time = now;
        process_knock(raw_val);
    }
}
