/* Розпакування однієї заповненої половини буфера у вольти. */
#include "esp_adc/adc_continuous.h"

#define VREF   3.3f
#define FS_MAX 4095.0f          /* 2¹² − 1 */

void process_block(const uint8_t *buf, uint32_t len)
{
    const adc_sample_t *s = (const adc_sample_t *)buf;
    uint32_t count = len / sizeof(adc_sample_t);   /* скільки вибірок у блоці */

    float sum = 0.0f;
    for (uint32_t i = 0; i < count; ++i) {
        float v = s[i].val * VREF / FS_MAX;        /* код → вольти */
        sum += v;
        /* калібрування, фільтр, запис у чергу — тут, не на шляху DMA */
    }
    float mean = sum / count;                       /* середнє по блоку */
    publish_mean(mean);
}

/* Задача: чекає сигнал від драйвера й тягне готові блоки. */
void adc_task(void *arg)
{
    adc_continuous_handle_t h = (adc_continuous_handle_t)arg;
    uint8_t  block[2048];
    uint32_t got = 0;
    for (;;) {
        /* блокуємось, доки DMA не наповнить половину буфера */
        if (adc_continuous_read(h, block, sizeof(block), &got, portMAX_DELAY) == ESP_OK)
            process_block(block, got);
    }
}
