#include "../include/quad_encoder_driver.h"

/**
 * Таблиця переходів FSM для декодування квадратурного сигналу.
 * Індекс формується як: (попередній_стан << 2) | поточний_стан.
 * Значення: +1 (CW), -1 (CCW), 0 (немає зміни або заборонений перехід/дребезг).
 */
static const int8_t ENCODER_FSM_LUT[16] = {
    [0]  =  0, // 00 -> 00 (немає руху)
    [1]  =  1, // 00 -> 01 (CW)
    [2]  = -1, // 00 -> 10 (CCW)
    [3]  =  0, // 00 -> 11 (заборонений діагональний перехід)
    [4]  = -1, // 01 -> 00 (CCW)
    [5]  =  0, // 01 -> 01 (немає руху)
    [6]  =  0, // 01 -> 10 (заборонений перехід)
    [7]  =  1, // 01 -> 11 (CW)
    [8]  =  1, // 10 -> 00 (CW)
    [9]  =  0, // 10 -> 01 (заборонений перехід)
    [10] =  0, // 10 -> 10 (немає руху)
    [11] = -1, // 10 -> 11 (CCW)
    [12] =  0, // 11 -> 00 (заборонений перехід)
    [13] = -1, // 11 -> 01 (CCW)
    [14] =  1, // 11 -> 10 (CW)
    [15] =  0  // 11 -> 11 (немає руху)
};

void quad_encoder_init(quad_encoder_t *enc, uint8_t initial_a, uint8_t initial_b) {
    if (!enc) return;

    uint8_t curr_state = ((initial_a & 0x01U) << 1) | (initial_b & 0x01U);
    enc->fsm.prev_state = curr_state;
    enc->fsm.position = 0;
    enc->fsm.step_accumulator = 0;

    enc->button.raw_state = 0;
    enc->button.debounced_state = 0;
    enc->button.last_debounce_ms = 0;
    enc->button.press_start_ms = 0;
    enc->button.long_press_handled = false;

    enc->last_read_position = 0;
}

void quad_encoder_update_phases(quad_encoder_t *enc, uint8_t phase_a, uint8_t phase_b) {
    if (!enc) return;

    uint8_t curr_state = ((phase_a & 0x01U) << 1) | (phase_b & 0x01U);
    uint8_t lut_index = (enc->fsm.prev_state << 2) | curr_state;

    int8_t increment = ENCODER_FSM_LUT[lut_index];
    if (increment != 0) {
        enc->fsm.position += increment;
        enc->fsm.prev_state = curr_state;
    } else if (curr_state == enc->fsm.prev_state) {
        // Стан не змінився
    } else {
        // Заборонений перехід (ігноруємо та оновлюємо стан для відновлення синхронізації)
        enc->fsm.prev_state = curr_state;
    }
}

quad_encoder_event_t quad_encoder_update_button(quad_encoder_t *enc, uint8_t raw_button_state, uint32_t current_time_ms) {
    if (!enc) return ENCODER_EVENT_NONE;

    quad_encoder_event_t event = ENCODER_EVENT_NONE;

    // Фіксація зміни сирого стану кнопки для скидання таймера антидребезгу
    if (raw_button_state != enc->button.raw_state) {
        enc->button.raw_state = raw_button_state;
        enc->button.last_debounce_ms = current_time_ms;
    }

    // Перевірка витримки часу для усунення брязкоту контактів
    if ((current_time_ms - enc->button.last_debounce_ms) >= ENCODER_BTN_DEBOUNCE_MS) {
        if (enc->button.raw_state != enc->button.debounced_state) {
            enc->button.debounced_state = enc->button.raw_state;

            if (enc->button.debounced_state == 1) {
                // Кнопку натиснуто
                enc->button.press_start_ms = current_time_ms;
                enc->button.long_press_handled = false;
            } else {
                // Кнопку відпущено
                if (!enc->button.long_press_handled) {
                    event = BUTTON_EVENT_SHORT_PRESS;
                }
            }
        }
    }

    // Перевірка утримання кнопки (довге натискання)
    if (enc->button.debounced_state == 1 && !enc->button.long_press_handled) {
        if ((current_time_ms - enc->button.press_start_ms) >= ENCODER_BTN_LONG_PRESS_MS) {
            enc->button.long_press_handled = true;
            event = BUTTON_EVENT_LONG_PRESS;
        }
    }

    return event;
}

int32_t quad_encoder_get_position(const quad_encoder_t *enc) {
    if (!enc) return 0;
    return enc->fsm.position;
}

int32_t quad_encoder_get_delta(quad_encoder_t *enc) {
    if (!enc) return 0;
    int32_t current_pos = enc->fsm.position;
    int32_t delta = current_pos - enc->last_read_position;
    enc->last_read_position = current_pos;
    return delta;
}
