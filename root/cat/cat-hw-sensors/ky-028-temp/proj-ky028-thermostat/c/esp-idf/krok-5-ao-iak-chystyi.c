#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

static const char *TAG = "ky028";
#define AO_CHANNEL  ADC_CHANNEL_6                // GPIO34 — ADC1

static adc_oneshot_unit_handle_t adc1;
static int      warmS    = 0;        // згладжене «тепло» (більше = тепліше)
static int      prevWarm = 0;        // попереднє згладжене — для швидкості
static uint32_t tPrev    = 0;

static uint32_t now_ms(void)  { return (uint32_t)(esp_timer_get_time() / 1000); }

static int read_warm(void) {
    int raw = 0;
    adc_oneshot_read(adc1, AO_CHANNEL, &raw);
    return 4095 - raw;                           // інверсія: більше = тепліше
}

void app_main(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    adc_oneshot_new_unit(&unit, &adc1);
    adc_oneshot_chan_cfg_t ch = { .bitwidth = ADC_BITWIDTH_12,
                                  .atten    = ADC_ATTEN_DB_12 };
    adc_oneshot_config_channel(adc1, AO_CHANNEL, &ch);

    warmS = prevWarm = read_warm();
    tPrev = now_ms();

    while (1) {
        warmS += (read_warm() - warmS) / 8;      // сильніше згладжування для тренду

        if (now_ms() - tPrev >= 500) {           // раз на пів секунди рахуємо швидкість
            int rate = warmS - prevWarm;         // зміна за інтервал (відносна!)
            const char *dir = rate > 2 ? "тепліє"
                            : rate < -2 ? "холоне"
                            : "стабільно";
            ESP_LOGI(TAG, "тренд: %s   швидкість (відносна): %d", dir, rate);
            prevWarm = warmS;
            tPrev = now_ms();
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
