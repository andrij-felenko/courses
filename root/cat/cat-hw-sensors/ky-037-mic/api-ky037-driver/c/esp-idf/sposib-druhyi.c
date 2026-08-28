#include "esp_adc/adc_oneshot.h"
#include "esp_timer.h"
#include "esp_log.h"
#include <math.h>

// adc1 і MIC_CHAN — з mic_begin() вище

static float measure_rms(void) {
    int v;
    // --- прохід 1: середнє (робоча точка) за вікно ---
    int64_t t0 = esp_timer_get_time();
    int64_t sum = 0;
    int     n = 0;
    while (esp_timer_get_time() - t0 < WINDOW_US) {
        adc_oneshot_read(adc1, MIC_CHAN, &v);
        sum += v;
        n++;
    }
    float mean = (float)sum / n;

    // --- прохід 2: сума квадратів відхилень від середнього ---
    t0 = esp_timer_get_time();
    float sum_sq = 0;
    int   n2 = 0;
    while (esp_timer_get_time() - t0 < WINDOW_US) {
        adc_oneshot_read(adc1, MIC_CHAN, &v);
        float d = v - mean;
        sum_sq += d * d;
        n2++;
    }
    return sqrtf(sum_sq / n2);        // RMS-відхилення в одиницях АЦП
}

void app_main(void) {
    mic_begin();
    while (1) ESP_LOGI("ky037", "%.1f", measure_rms());
}
