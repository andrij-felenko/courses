#include "esp_adc/adc_continuous.h"
#include "soc/soc_caps.h"

#define VREF    3.3f
#define ADC_MAX 4095.0f            /* 2¹² − 1 */

/* Власні макроси доступу — розводяться на потрібний член структури під час
   компіляції. TYPE1 на класичному ESP32/S2, TYPE2 на решті чіпів. */
#if CONFIG_IDF_TARGET_ESP32 || CONFIG_IDF_TARGET_ESP32S2
    #define GET_CHANNEL(p)  ((p)->type1.channel)
    #define GET_DATA(p)     ((p)->type1.data)
#else
    #define GET_CHANNEL(p)  ((p)->type2.channel)
    #define GET_DATA(p)     ((p)->type2.data)
#endif

/* Розбір одного блоку. Крок масиву — з константи чіпа, НЕ з sizeof:
   на TYPE1 це 2 байти, на TYPE2 — 4; хардкод зламав би один із випадків. */
void process_block(const uint8_t *buf, uint32_t len)
{
    /* скільки вибірок у блоці — ділимо на РОЗМІР РЕЗУЛЬТАТУ цього чіпа */
    uint32_t count = len / SOC_ADC_DIGI_RESULT_BYTES;

    for (uint32_t i = 0; i < count; ++i) {
        /* наводимося на i-ту вибірку через розмір результату,
           а не через індекс масиву вигаданого типу */
        const adc_digi_output_data_t *p =
            (const adc_digi_output_data_t *)&buf[i * SOC_ADC_DIGI_RESULT_BYTES];

        uint32_t ch   = GET_CHANNEL(p);
        uint32_t code = GET_DATA(p);

        /* Скільки каналів має ADC1 на цьому чіпі; більший номер —
           службове/сміттєве слово, пропускаємо. */
        if (ch >= SOC_ADC_CHANNEL_NUM(ADC_UNIT_1)) continue;

        float v = code * VREF / ADC_MAX;   /* код → вольти */
        route_sample(ch, v);               /* калібрування/фільтр/черга — тут */
    }
}
