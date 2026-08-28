#include "esp_sleep.h"
#include "ulp_riscv.h"
#include "ulp_adc.h"
#include "ulp_main.h"   /* згенерований заголовок: оголошує ulp_adc_threshold,
                           ulp_wakeup_result і т. д.                         */

/* Символи бінарника ULP — лінкер підставляє автоматично */
extern const uint8_t ulp_main_bin_start[] asm("_binary_ulp_main_bin_start");
extern const uint8_t ulp_main_bin_end[]   asm("_binary_ulp_main_bin_end");

static void init_ulp_program(void);

void app_main(void)
{
    /* Дізнаємось, чому прокинулись */
    esp_sleep_wakeup_cause_t causes = esp_sleep_get_wakeup_causes();

    if (!(causes & BIT(ESP_SLEEP_WAKEUP_ULP))) {
        /* Перший старт або пробудження НЕ від ULP — заливаємо й запускаємо ULP */
        init_ulp_program();
    } else {
        /* ULP розбудив нас: є значення вище порогу */
        printf("ULP wakeup! value=%ld threshold=%lu\n",
               (long)ulp_wakeup_result, (unsigned long)ulp_adc_threshold);
    }

    /* Тримаємо RTC-периферію живою — інакше АЦП-конфіг загубиться в сні.
       Це типова пастка: без цього рядка ULP читатиме сміття.              */
    ESP_ERROR_CHECK(esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH,
                                        ESP_PD_OPTION_ON));
    esp_sleep_enable_ulp_wakeup();
    esp_deep_sleep_start();
}

static void init_ulp_program(void)
{
    /* Конфігуруємо АЦП під ULP-RISC-V */
    ulp_adc_cfg_t cfg = {
        .adc_n   = EXAMPLE_ADC_UNIT,
        .channel = EXAMPLE_ADC_CHANNEL,
        .width   = ADC_BITWIDTH_DEFAULT,
        .atten   = ADC_ATTEN_DB_12,
        .ulp_mode = ADC_ULP_MODE_RISCV,
    };
    ESP_ERROR_CHECK(ulp_adc_init(&cfg));

    /* Заливаємо бінарник ULP у RTC slow memory */
    ESP_ERROR_CHECK(ulp_riscv_load_binary(ulp_main_bin_start,
                        ulp_main_bin_end - ulp_main_bin_start));

    /* Таймер: ULP прокидатиметься кожні 20 000 мкс = 20 мс */
    ulp_set_wakeup_period(0, 20000);

    /* Запускаємо ULP */
    ESP_ERROR_CHECK(ulp_riscv_run());
}
