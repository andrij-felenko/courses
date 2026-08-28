#include <stdint.h>
#include "ulp_riscv_utils.h"
#include "ulp_riscv_adc_ulp_core.h"

/* АЦП-канал і поріг — підганяємо під свій давач */
#define EXAMPLE_ADC_UNIT    ADC_UNIT_1
#define EXAMPLE_ADC_CHANNEL ADC_CHANNEL_0
/* 2000 — сирий код АЦП; при atten 12 dB і ADC_BITWIDTH_DEFAULT
   це приблизно 1.75 В (як у канонічному прикладі ESP-IDF).     */
#define EXAMPLE_ADC_THRESHOLD 2000

/* Глобальні змінні, доступні головному ядру через префікс ulp_:
   ulp_adc_threshold і ulp_wakeup_result                        */
uint32_t adc_threshold = EXAMPLE_ADC_THRESHOLD;
int32_t  wakeup_result = 0;

int main(void)
{
    /* Читаємо АЦП у RTC-домені (не esp_adc — той у high-power домені). */
    int32_t v = ulp_riscv_adc_read_channel(EXAMPLE_ADC_UNIT, EXAMPLE_ADC_CHANNEL);

    if (v > (int32_t)adc_threshold) {
        wakeup_result = v;
        ulp_riscv_wakeup_main_processor(); /* піднімаємо сигнал пробудження */
    }

    return 0;
    /* Після return 0: ulp_riscv_halt() викликається АВТОМАТИЧНО —
       ULP паркується до наступного тіку RTC-таймера.
       Ставити while(1) або явний halt тут не потрібно і шкідливо. */
}
