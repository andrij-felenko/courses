// Той самий автоповтор на ESP-IDF: таймаут черги і є тиком власного темпу
#include "driver/rmt_rx.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_timer.h"

#define MY_REMOTE  0x00
#define REPEAT_MS  120                  // ВЛАСНИЙ темп автоповтору, мс
#define RELEASE_MS 250                  // тиша довша за це = кнопку відпустили
enum { BTN_UP = 0x15, BTN_DOWN = 0x07 };

static uint8_t  brightness   = 128;
static uint16_t held_command = 0;       // яку кнопку тримають (0 = жодну)

static uint32_t now_ms(void) { return (uint32_t)(esp_timer_get_time() / 1000); }

// одна «дія кнопки» — крок регулювання
static void step_button(uint16_t cmd) {
    if (cmd == BTN_UP   && brightness <= 250) brightness += 5;
    if (cmd == BTN_DOWN && brightness >= 5)   brightness -= 5;
    apply_brightness();
}

void app_main(void) {
    ir_rx_start();                      // RMT + LEDC, налаштовані як у кроці 2
    uint32_t last_action = 0, last_frame = 0;
    rmt_rx_done_event_data_t ev;

    while (1) {
        // 1) чекаємо кадр НЕ довше за REPEAT_MS — таймаут і є тиком автоповтору
        if (xQueueReceive(q, &ev, pdMS_TO_TICKS(REPEAT_MS)) == pdPASS) {
            uint16_t addr = 0, cmd = 0; bool repeat = false;
            if (nec_parse(ev.received_symbols, ev.num_symbols, &addr, &cmd, &repeat)
                && addr == MY_REMOTE) {
                last_frame = now_ms();  // будь-який наш кадр = «кнопка ще жива»
                if (!repeat) {          // новий натиск: діємо одразу й беремо «на утримання»
                    held_command = cmd;
                    step_button(cmd);
                    last_action = now_ms();
                }
            }
            rmt_receive(rx, syms, sizeof(syms), &rc);
        }

        // 2) поки кнопку тримають — крутимо значення СВОЇМ темпом
        if (held_command && now_ms() - last_action >= REPEAT_MS) {
            step_button(held_command);
            last_action = now_ms();
        }

        // 3) якщо кадрів/повторів давно нема — кнопку відпустили
        if (held_command && now_ms() - last_frame > RELEASE_MS) held_command = 0;
    }
}
