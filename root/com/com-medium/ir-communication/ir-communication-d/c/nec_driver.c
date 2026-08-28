/* nec_driver.c - Реалізація декодера та енкодера NEC мовою C */
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t address;
    uint8_t command;
    bool is_repeat;
} nec_msg_t;

typedef enum {
    STATE_IDLE,
    STATE_LEADER_BURST,
    STATE_LEADER_SPACE,
    STATE_DATA_BIT
} nec_fsm_state_t;

static nec_fsm_state_t g_state = STATE_IDLE;
static uint32_t g_last_time_us = 0;
static uint32_t g_bit_buffer = 0;
static uint8_t  g_bit_count = 0;

// Обробник перепаду сигналу на вході від TSOP
bool nec_decode_edge(uint32_t now_us, bool pin_level, nec_msg_t *out_msg) {
    uint32_t delta = now_us - g_last_time_us;
    g_last_time_us = now_us;

    switch (g_state) {
        case STATE_IDLE:
            if (!pin_level) { // Спад напруги: початок світла
                g_state = STATE_LEADER_BURST;
            }
            break;

        case STATE_LEADER_BURST:
            if (pin_level) { // Наростання напруги: кінець спалаху 9 мс
                if (delta >= 7500 && delta <= 10500) {
                    g_state = STATE_LEADER_SPACE;
                } else {
                    g_state = STATE_IDLE;
                }
            }
            break;

        case STATE_LEADER_SPACE:
            if (!pin_level) { // Спад: кінець паузи преамбули
                if (delta >= 3800 && delta <= 5200) {
                    g_bit_buffer = 0;
                    g_bit_count = 0;
                    g_state = STATE_DATA_BIT;
                } else if (delta >= 1800 && delta <= 2700) {
                    // Код повтору
                    if (out_msg) {
                        out_msg->is_repeat = true;
                    }
                    g_state = STATE_IDLE;
                    return true;
                } else {
                    g_state = STATE_IDLE;
                }
            }
            break;

        case STATE_DATA_BIT:
            if (pin_level) {
                // Перевірка тривалості світлового спалаху біта (~560 мкс)
                if (delta < 350 || delta > 800) {
                    g_state = STATE_IDLE;
                }
            } else {
                // Вимірювання тривалості паузи між спалахами
                if (delta >= 400 && delta <= 750) {
                    // Логічний '0'
                    g_bit_count++;
                } else if (delta >= 1400 && delta <= 2000) {
                    // Логічна '1'
                    g_bit_buffer |= ((uint32_t)1 << g_bit_count);
                    g_bit_count++;
                } else {
                    g_state = STATE_IDLE;
                    break;
                }

                if (g_bit_count >= 32) {
                    uint8_t addr     = (uint8_t)(g_bit_buffer & 0xFF);
                    uint8_t addr_inv = (uint8_t)((g_bit_buffer >> 8) & 0xFF);
                    uint8_t cmd      = (uint8_t)((g_bit_buffer >> 16) & 0xFF);
                    uint8_t cmd_inv  = (uint8_t)((g_bit_buffer >> 24) & 0xFF);

                    g_state = STATE_IDLE;
                    if ((addr == (uint8_t)~addr_inv) && (cmd == (uint8_t)~cmd_inv)) {
                        if (out_msg) {
                            out_msg->address = addr;
                            out_msg->command = cmd;
                            out_msg->is_repeat = false;
                        }
                        return true;
                    }
                }
            }
            break;
    }
    return false;
}
