// Те саме на ESP-IDF 5.x: кадр ловить периферія RMT, NEC розбираємо самі
#include "driver/rmt_rx.h"
#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_log.h"

#define IR_GPIO   GPIO_NUM_4          // будь-який GPIO, придатний під вхід RMT
#define MY_REMOTE 0x00                // адреса ТВОГО пульта (знята скелетом)

// коди кнопок ЦЬОГО пульта
enum { BTN_1 = 0x45, BTN_2 = 0x46, BTN_PLAY = 0x40, BTN_UP = 0x15, BTN_DOWN = 0x07 };

static const char *TAG = "ir-menu";
static uint8_t brightness = 128;      // стан, яким керуємо (0..255)

static void apply_brightness(void) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, brightness);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
    ESP_LOGI(TAG, "яскравість = %u", brightness);
}

static bool near_us(uint32_t d, uint32_t want) { return d + 250 > want && d < want + 250; }

// розбір NEC із таймінгів RMT; на кадрі-повторі поля беремо з попереднього кадру
static bool nec_parse(const rmt_symbol_word_t *s, size_t n,
                      uint16_t *addr, uint16_t *cmd, bool *repeat) {
    static uint16_t last_addr, last_cmd;
    if (n < 2 || !near_us(s[0].duration0, 9000)) return false;       // преамбула 9 мс
    if (near_us(s[0].duration1, 2250)) {                             // куций кадр-повтор
        *addr = last_addr; *cmd = last_cmd; *repeat = true; return true;
    }
    if (!near_us(s[0].duration1, 4500) || n < 33) return false;
    uint32_t bits = 0;
    for (int i = 0; i < 32; i++) bits |= (uint32_t)(s[i + 1].duration1 > 1000) << i;
    *addr = last_addr = bits & 0xFF;          // молодшим бітом уперед: addr, ~addr, cmd, ~cmd
    *cmd  = last_cmd  = (bits >> 16) & 0xFF;
    *repeat = false;
    return true;
}

static bool IRAM_ATTR rx_done(rmt_channel_handle_t ch,
                              const rmt_rx_done_event_data_t *ev, void *q) {
    BaseType_t woken = pdFALSE;
    xQueueSendFromISR((QueueHandle_t)q, ev, &woken);
    return woken == pdTRUE;
}

static QueueHandle_t        q;
static rmt_channel_handle_t rx;
static rmt_symbol_word_t    syms[64];
static rmt_receive_config_t rc = { .signal_range_min_ns = 1250,
                                   .signal_range_max_ns = 12000000 };

void app_main(void) {
    ledc_init_pwm();                          // таймер+канал LEDC_CHANNEL_0 під світлодіод
    q = xQueueCreate(4, sizeof(rmt_rx_done_event_data_t));
    rmt_rx_channel_config_t rx_cfg = {
        .clk_src         = RMT_CLK_SRC_DEFAULT,
        .resolution_hz   = 1000000,           // 1 тік = 1 мкс
        .mem_block_symbols = 64,
        .gpio_num        = IR_GPIO,
    };
    ESP_ERROR_CHECK(rmt_new_rx_channel(&rx_cfg, &rx));
    rmt_rx_event_callbacks_t cbs = { .on_recv_done = rx_done };
    ESP_ERROR_CHECK(rmt_rx_register_event_callbacks(rx, &cbs, q));
    ESP_ERROR_CHECK(rmt_enable(rx));
    apply_brightness();
    ESP_ERROR_CHECK(rmt_receive(rx, syms, sizeof(syms), &rc));   // «озброїли» приймач

    rmt_rx_done_event_data_t ev;
    while (xQueueReceive(q, &ev, portMAX_DELAY) == pdPASS) {
        uint16_t addr = 0, cmd = 0; bool repeat = false;
        // чужий пульт? — ігноруємо, але приймач переозброїти ОБОВ'ЯЗКОВО (нижче)
        if (nec_parse(ev.received_symbols, ev.num_symbols, &addr, &cmd, &repeat)
            && addr == MY_REMOTE) {
            switch (cmd) {
            case BTN_UP:   if (brightness <= 245) brightness += 10; apply_brightness(); break;
            case BTN_DOWN: if (brightness >= 10)  brightness -= 10; apply_brightness(); break;
            case BTN_PLAY: brightness = brightness ? 0 : 128;       apply_brightness(); break;
            case BTN_1: ESP_LOGI(TAG, "режим 1"); break;
            case BTN_2: ESP_LOGI(TAG, "режим 2"); break;
            default:    ESP_LOGW(TAG, "невідома кнопка: 0x%02X", cmd); break;
            }
        }
        rmt_receive(rx, syms, sizeof(syms), &rc);   // ← тут аналог resume()
    }
}
