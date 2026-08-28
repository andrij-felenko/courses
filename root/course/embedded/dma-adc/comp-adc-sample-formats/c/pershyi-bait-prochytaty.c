#include "esp_adc/adc_continuous.h"
#include "soc/soc_caps.h"

/* Навести на найперше слово буфера — через РОЗМІР РЕЗУЛЬТАТУ цього чіпа,
   а не через тип вигаданої структури. */
const adc_digi_output_data_t *p = (const void *)&buf[0];

/* Дістати код і канал із того члена структури, що дійсний на цьому чіпі. */
#if CONFIG_IDF_TARGET_ESP32 || CONFIG_IDF_TARGET_ESP32S2
    uint32_t code = p->type1.data;      /* TYPE1: 16-бітне слово */
    uint32_t ch   = p->type1.channel;
#else
    uint32_t code = p->type2.data;      /* TYPE2: 32-бітне слово */
    uint32_t ch   = p->type2.channel;
#endif

float v = code * 3.3f / 4095.0f;        /* код → вольти (перше наближення) */
