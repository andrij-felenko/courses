// Монітор струму на ESP32: шунт 5 мОм + підсилювач G=50 + 12-біт АЦП
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

#define R_SHUNT 0.005f            // Ом
#define GAIN    50.0f             // коефіцієнт підсилювача струму
#define VREF    3.3f              // опорна напруга АЦП, В
#define ADC_MAX 4095              // 12 біт

static const char *TAG = "isense";
static adc_oneshot_unit_handle_t adc1;
static float i_zero = 0.0f;       // калібрований нуль (привид від offset), А
static double charge_mAh = 0.0;   // накопичений заряд

// GPIO34 на ESP32 — це ADC1 канал 6
void isense_init(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));
    adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_11, .bitwidth = ADC_BITWIDTH_12 };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, ADC_CHANNEL_6, &ch));
}

// Перевести «сирий» код АЦП у струм через шунт (закон Ома, назад через тракт)
float read_current(void) {
    int raw = 0;
    esp_err_t err = adc_oneshot_read(adc1, ADC_CHANNEL_6, &raw);
    if (err != ESP_OK) { ESP_LOGE(TAG, "ADC: %s", esp_err_to_name(err)); return 0.0f; }
    float v_adc = (float)raw / ADC_MAX * VREF;    // напруга на вході АЦП, В
    float v_sh  = v_adc / GAIN;                   // спад на самому шунті, В
    return v_sh / R_SHUNT - i_zero;               // I = V/R, мінус нуль
}

// Калібрування нуля: викликати, коли точно відомо, що струму немає
void calibrate_zero(void) {
    float acc = 0.0f;
    for (int k = 0; k < 64; k++) { acc += read_current() + i_zero; vTaskDelay(pdMS_TO_TICKS(2)); }
    i_zero = acc / 64.0f;                         // усереднений привид від offset
}

// Інтегрувати заряд: Q += I·Δt  (coulomb counter)
void accumulate_charge(float dt_s) {
    charge_mAh += (double)read_current() * dt_s / 3.6;   // А·с → мА·год: ділимо на 3.6
}
