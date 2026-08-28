// ── Монітор просадки UBEC-шини. ESP-IDF (adc_oneshot + калібрування) ──
// Дільник зменшує 5 В до безпечного для АЦП вікна; калібрування віддає
// мілівольти на піні з поправкою на заводський розкид чипа.
// Дільник: R1=15к (згори, від шини), R2=10к (до землі) → k = 0.4.
//   Uвузол = 5.0 · 0.4 = 2.0 В  (у лінійній зоні АЦП ESP32)
//   назад:  Uшини = Uвузол · (R1+R2)/R2 = Uвузол · 2.5
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
#include "esp_timer.h"
#include "esp_log.h"

#define RAIL_CH     ADC_CHANNEL_6      // GPIO34 на ADC1: вхід-лише, зручний для АЦП
#define DIV         2.5f               // (15к+10к)/10к
#define BROWNOUT_MV 4600               // поріг тривоги, мВ на шині
static const char *TAG = "rail";

static adc_oneshot_unit_handle_t adc1;
static adc_cali_handle_t cali;

void rail_monitor_init(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));
    adc_oneshot_chan_cfg_t ch = {           // послаблення 12 дБ → вікно ~0..3.1 В
        .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, RAIL_CH, &ch));

    adc_cali_line_fitting_config_t c = {    // класичний ESP32 калібрують прямою
        .unit_id = ADC_UNIT_1, .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_DEFAULT };
    ESP_ERROR_CHECK(adc_cali_create_scheme_line_fitting(&c, &cali));
}

uint16_t rail_read_mv(void) {
    int acc = 0, raw = 0, mv = 0;
    for (int i = 0; i < 8; i++) {           // усереднення 8 вибірок — прибрати шум
        ESP_ERROR_CHECK(adc_oneshot_read(adc1, RAIL_CH, &raw));
        acc += raw;
    }
    ESP_ERROR_CHECK(adc_cali_raw_to_voltage(cali, acc / 8, &mv));  // калібровані мВ
    return (uint16_t)(mv * DIV);            // назад у мілівольти шини
}

// Викликати нечасто (напр. раз на 100 мс) із задачі — не блокує.
void rail_monitor_service(void) {
    static int64_t last = 0;
    int64_t now = esp_timer_get_time() / 1000;
    if (now - last < 100) return;
    last = now;

    uint16_t mv = rail_read_mv();
    if (mv < BROWNOUT_MV) {
        ESP_LOGW(TAG, "BROWNOUT! шина = %u мВ — рознеси рухи / послаб навантаження", mv);
        // тут-таки реакція: НЕ починати нову розкладку серв, поки шина не встане,
        // запалити червоний LED, знизити кількість одночасних серв…
    }
}
