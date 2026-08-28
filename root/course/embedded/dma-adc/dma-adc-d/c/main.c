#include "esp_adc/adc_continuous.h"
#include "soc/soc_caps.h"

#define VREF    3.3f
#define ADC_MAX 4095.0f            /* 2¹² − 1, розрядність 12 біт */

/* Власні макроси доступу — самі розводяться на потрібне поле під час компіляції.
   На класичному ESP32/S2 слово у форматі type1, на решті чіпів — type2. */
#if CONFIG_IDF_TARGET_ESP32 || CONFIG_IDF_TARGET_ESP32S2
    #define GET_CHANNEL(p)  ((p)->type1.channel)
    #define GET_DATA(p)     ((p)->type1.data)
#else
    #define GET_CHANNEL(p)  ((p)->type2.channel)
    #define GET_DATA(p)     ((p)->type2.data)
#endif

/* Розбір одного блоку. Крок масиву — з константи чіпа, НЕ з sizeof вигаданого union:
   на TYPE1 це 2 байти, на TYPE2 — 4, і хардкод зламав би один із випадків. */
void process_block(const uint8_t *buf, uint32_t len)
{
    /* скільки вибірок у блоці — ділимо на РОЗМІР РЕЗУЛЬТАТУ ЦЬОГО чіпа */
    uint32_t count = len / SOC_ADC_DIGI_RESULT_BYTES;

    for (uint32_t i = 0; i < count; ++i) {
        /* наводимося на i-ту вибірку через розмір результату, а не через індекс масиву union */
        const adc_digi_output_data_t *p =
            (const adc_digi_output_data_t *)&buf[i * SOC_ADC_DIGI_RESULT_BYTES];

        uint32_t ch   = GET_CHANNEL(p);
        uint32_t code = GET_DATA(p);

        /* SOC_ADC_CHANNEL_NUM(ADC_UNIT_1) — скільки каналів у ADC1 на цьому чіпі;
           більший номер = службове/сміттєве слово, пропускаємо */
        if (ch >= SOC_ADC_CHANNEL_NUM(ADC_UNIT_1)) continue;

        float v = code * VREF / ADC_MAX;           /* код → вольти (перше наближення) */
        route_sample(ch, v);                        /* калібрування/фільтр/черга — тут, не в ISR */
    }
}

/* Колбек переповнення: сигналить, що f_s швидша за темп обробки. В ISR — тільки прапорець. */
static volatile uint32_t g_overflows = 0;
static bool IRAM_ATTR on_pool_ovf(adc_continuous_handle_t h,
                                  const adc_continuous_evt_data_t *e, void *arg)
{
    g_overflows++;         /* нарощуємо лічильник; важку роботу — поза ISR */
    return false;          /* не будимо задачу вищого пріоритету */
}

/* Задача: блокується, доки драйвер не віддасть когерентний блок (копію з DMA-кільця). */
void adc_task(void *arg)
{
    adc_continuous_handle_t h = (adc_continuous_handle_t)arg;
    uint8_t  block[1024];
    uint32_t got = 0;
    for (;;) {
        esp_err_t r = adc_continuous_read(h, block, sizeof(block), &got, portMAX_DELAY);
        if (r == ESP_OK) {
            process_block(block, got);
        } else if (r == ESP_ERR_INVALID_STATE) {
            /* пул переповнено: обробка відстає від вибірки — збільшити буфер або знизити f_s */
            handle_overrun();
        }
    }
}
