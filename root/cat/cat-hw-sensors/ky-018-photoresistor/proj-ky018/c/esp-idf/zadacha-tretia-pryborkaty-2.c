#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "ldr";
#define LDR_CHAN  ADC_CHANNEL_6     // GPIO34
#define N         16                // розмір вікна

static int      buf[N];             // кільцевий буфер відліків
static uint8_t  idx = 0;            // куди писати наступний
static long     sum = 0;            // поточна сума вмісту буфера
static bool     filled = false;     // чи буфер уже повний

static int moving_average(int raw) {
  sum -= buf[idx];                  // викинути найдавніший відлік із суми
  buf[idx] = raw;                   // покласти новий на його місце
  sum += raw;                       // додати новий у суму
  idx = (idx + 1) % N;              // зсунути вказівник по колу
  if (idx == 0) filled = true;
  uint8_t count = filled ? N : idx; // поки не заповнилось — ділимо на реальну кількість
  return count ? (int)(sum / count) : raw;
}

void app_main(void) {
  adc_oneshot_unit_handle_t adc1;
  adc_oneshot_unit_init_cfg_t init = { .unit_id = ADC_UNIT_1 };
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&init, &adc1));
  adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_12 };
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, LDR_CHAN, &ch));

  for (;;) {
    int raw = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(adc1, LDR_CHAN, &raw));
    ESP_LOGI(TAG, "%d", moving_average(raw));
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}
