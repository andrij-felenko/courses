/* nec_transceiver.c - Реалізація автомата станів декодера */
#include "nec_transceiver.h"

void nec_receiver_init(nec_receiver_t *rx) {
    rx->state = NEC_RX_STATE_IDLE;
    rx->last_capture_us = 0;
    rx->raw_data = 0;
    rx->bit_index = 0;
    rx->packet_ready = false;
}

void nec_receiver_on_edge(nec_receiver_t *rx, uint32_t timestamp_us, bool pin_state) {
    uint32_t duration = timestamp_us - rx->last_capture_us;
    rx->last_capture_us = timestamp_us;

    switch (rx->state) {
        case NEC_RX_STATE_IDLE:
            if (!pin_state) { // Спад у LOW: початок світлової пачки
                rx->state = NEC_RX_STATE_LEADER_BURST;
            }
            break;

        case NEC_RX_STATE_LEADER_BURST:
            if (pin_state) { // Наростання у HIGH: кінець пачки 9 мс
                if (duration >= 7500 && duration <= 10500) {
                    rx->state = NEC_RX_STATE_LEADER_SPACE;
                } else {
                    rx->state = NEC_RX_STATE_IDLE;
                }
            }
            break;

        case NEC_RX_STATE_LEADER_SPACE:
            if (!pin_state) { // Спад у LOW: кінець паузи преамбули
                if (duration >= 3800 && duration <= 5200) {
                    // Стандартний кадр даних
                    rx->raw_data = 0;
                    rx->bit_index = 0;
                    rx->state = NEC_RX_STATE_BIT_PULSE;
                } else if (duration >= 1800 && duration <= 2700) {
                    // Код повтору (Repeat code)
                    rx->packet.is_repeat = true;
                    rx->packet_ready = true;
                    rx->state = NEC_RX_STATE_IDLE;
                } else {
                    rx->state = NEC_RX_STATE_IDLE;
                }
            }
            break;

        case NEC_RX_STATE_BIT_PULSE:
            if (pin_state) { // Наростання у HIGH: кінець бітового спалаху 560 мкс
                if (duration >= 350 && duration <= 750) {
                    rx->state = NEC_RX_STATE_BIT_SPACE;
                } else {
                    rx->state = NEC_RX_STATE_IDLE;
                }
            }
            break;

        case NEC_RX_STATE_BIT_SPACE:
            if (!pin_state) { // Спад у LOW: вимірювання тривалості паузи
                if (duration >= 400 && duration <= 750) {
                    // Логічний 0 (пауза ~560 мкс)
                    rx->bit_index++;
                } else if (duration >= 1400 && duration <= 2000) {
                    // Логічна 1 (пауза ~1690 мкс)
                    rx->raw_data |= ((uint32_t)1 << rx->bit_index);
                    rx->bit_index++;
                } else {
                    rx->state = NEC_RX_STATE_IDLE;
                    break;
                }

                if (rx->bit_index >= 32) {
                    // Прийнято всі 32 біти кадру
                    rx->packet.address     = (uint8_t)(rx->raw_data & 0xFF);
                    rx->packet.address_inv = (uint8_t)((rx->raw_data >> 8) & 0xFF);
                    rx->packet.command     = (uint8_t)((rx->raw_data >> 16) & 0xFF);
                    rx->packet.command_inv = (uint8_t)((rx->raw_data >> 24) & 0xFF);
                    rx->packet.is_repeat   = false;

                    // Валідація цілісності
                    if ((rx->packet.address == (uint8_t)~rx->packet.address_inv) &&
                        (rx->packet.command == (uint8_t)~rx->packet.command_inv)) {
                        rx->packet_ready = true;
                    }
                    rx->state = NEC_RX_STATE_IDLE;
                } else {
                    rx->state = NEC_RX_STATE_BIT_PULSE;
                }
            }
            break;
    }
}

bool nec_receiver_get_packet(nec_receiver_t *rx, nec_packet_t *out_packet) {
    if (rx->packet_ready) {
        *out_packet = rx->packet;
        rx->packet_ready = false;
        return true;
    }
    return false;
}
