#include <string.h>
#include "driver/uart.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// ── Словник подій: ID замість рядків ──────────────────────────────────────
typedef enum {
    LOG_BOOT     = 0,   // "boot"
    LOG_TEMP     = 1,   // "temp=%d mV"
    LOG_VBAT_LOW = 2,   // "VBAT low %d"
} log_id_t;

#define BLOG_UART  UART_NUM_0

// ── Кадр збираємо в буфері й віддаємо драйверу одним записом ──────────────
static void blog(uint8_t id, const void *args, uint8_t n) {
    uint8_t f[4 + 8];                        // маркер+id+n+аргументи+XOR
    uint8_t xor_sum = 0x7E ^ id ^ n;
    f[0] = 0x7E;                             // маркер-початок (ресинхронізація)
    f[1] = id;
    f[2] = n;
    if (n) memcpy(&f[3], args, n);
    for (uint8_t i = 0; i < n; i++) xor_sum ^= f[3 + i];
    f[3 + n] = xor_sum;                      // контрольний байт (XOR усього кадру)
    uart_write_bytes(BLOG_UART, f, 4 + n);
}

// ── Макрос: одна змінна, sizeof автоматично ───────────────────────────────
#define BLOG(id, val)  do { typeof(val) _v = (val); blog((id), &_v, sizeof(_v)); } while (0)

// ── Використання ──────────────────────────────────────────────────────────
void app_main(void) {
    uart_config_t cfg = {
        .baud_rate  = 115200,           .data_bits = UART_DATA_8_BITS,
        .parity     = UART_PARITY_DISABLE, .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl  = UART_HW_FLOWCTRL_DISABLE, .source_clk = UART_SCLK_DEFAULT,
    };
    uart_param_config(BLOG_UART, &cfg);
    uart_driver_install(BLOG_UART, 256, 512, 0, NULL, 0);
    blog(LOG_BOOT, NULL, 0);                 // подія без аргументів (n=0)

    adc_oneshot_unit_handle_t adc;
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    adc_oneshot_new_unit(&unit, &adc);
    adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12,
                                  .bitwidth = ADC_BITWIDTH_DEFAULT };
    adc_oneshot_config_channel(adc, ADC_CHANNEL_6, &ch);
    adc_oneshot_config_channel(adc, ADC_CHANNEL_7, &ch);

    while (1) {
        int raw = 0;
        adc_oneshot_read(adc, ADC_CHANNEL_6, &raw);
        int16_t temp_mv = (int16_t)(raw * 3300 / 4095);  // грубо, без калібрування
        BLOG(LOG_TEMP, temp_mv);             // int16_t → 2 байти сирих у кадр
        // якщо напруга критична — сигналізуємо
        adc_oneshot_read(adc, ADC_CHANNEL_7, &raw);
        int16_t vbat_mv = (int16_t)(raw * 3300 / 4095);
        if (vbat_mv < 3300) {
            BLOG(LOG_VBAT_LOW, vbat_mv);
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
