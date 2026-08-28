#include "esp_adc/adc_oneshot.h"

// Ловимо МІНІМУМ напруги живлення протягом вікна вимірювання.
// (3V3 подано на пін АЦП через дільник — АЦП ESP32 не бачить понад ~3.1 В напряму.)
static int measure_vdd_min_mv(adc_oneshot_unit_handle_t adc, adc_channel_t ch,
                              int window_ms, int divider_num, int divider_den)
{
    int min_raw = 1 << 30;
    int64_t t_end = esp_timer_get_time() + (int64_t)window_ms * 1000;
    while (esp_timer_get_time() < t_end) {
        int raw = 0;
        if (adc_oneshot_read(adc, ch, &raw) == ESP_OK && raw < min_raw) {
            min_raw = raw;
        }
        // без затримки: беремо якомога густіше, щоб не проґавити вузький провал
    }
    // raw → мВ на піні (для 12-біт і опори ~3.3 В шкала ≈ 3300/4095 мВ на відлік),
    // тоді назад через дільник до реальної 3V3:
    int mv_pin = (min_raw * 3300) / 4095;
    return mv_pin * divider_den / divider_num;
}
