#include "encoder_reader.h"
#include "servo_pwm.h"
#include <stddef.h>

/**
 * @file encoder_reader.c
 * @brief Реалізація декодера квадратурного енкодера.
 *
 * Табличний декодер 4-станового коду Грея із цифровим пригніченням контактного брязкоту.
 */

/* Таблиця переходів квадратурного енкодера (-1: проти годинникової, +1: за годинниковою, 0: немає руху / помилка) */
static const int8_t g_encoder_table[16] = {
     0,  1, -1,  0,
    -1,  0,  0,  1,
     1,  0,  0, -1,
     0, -1,  1,  0
};

void encoder_init(encoder_state_t *enc, int32_t min_pos, int32_t max_pos, uint16_t pulse_step_us)
{
    if (enc == NULL) {
        return;
    }

    enc->min_position = min_pos;
    enc->max_position = max_pos;
    enc->pulse_step_us = (pulse_step_us > 0) ? pulse_step_us : 10U;
    
    /* Встановити нейтральну позицію по центру */
    enc->position = (min_pos + max_pos) / 2;

    enc->raw_pin_a = false;
    enc->raw_pin_b = false;
    enc->debounced_pin_a = false;
    enc->debounced_pin_b = false;
    
    enc->count_a = 0;
    enc->count_b = 0;
    enc->prev_state = 0;
}

bool encoder_update_pins(encoder_state_t *enc, bool raw_a, bool raw_b)
{
    if (enc == NULL) {
        return false;
    }

    /* 1. Алгоритм цифрового пригнічення брязкоту контактів (Debounce Filtering) */
    if (raw_a == enc->raw_pin_a) {
        if (enc->count_a < ENCODER_DEBOUNCE_THRESHOLD_SAMPLES) {
            enc->count_a++;
            if (enc->count_a == ENCODER_DEBOUNCE_THRESHOLD_SAMPLES) {
                enc->debounced_pin_a = raw_a;
            }
        }
    } else {
        enc->raw_pin_a = raw_a;
        enc->count_a = 0;
    }

    if (raw_b == enc->raw_pin_b) {
        if (enc->count_b < ENCODER_DEBOUNCE_THRESHOLD_SAMPLES) {
            enc->count_b++;
            if (enc->count_b == ENCODER_DEBOUNCE_THRESHOLD_SAMPLES) {
                enc->debounced_pin_b = raw_b;
            }
        }
    } else {
        enc->raw_pin_b = raw_b;
        enc->count_b = 0;
    }

    /* 2. Декодування квадрантного стану */
    uint8_t current_state = ((uint8_t)enc->debounced_pin_a << 1) | ((uint8_t)enc->debounced_pin_b & 0x01U);
    
    /* Індекс таблиці переходу = (попередній стан << 2) | поточний стан */
    uint8_t table_index = (enc->prev_state << 2) | current_state;
    int8_t direction = g_encoder_table[table_index & 0x0FU];

    enc->prev_state = current_state;

    if (direction != 0) {
        int32_t new_pos = enc->position + direction;
        
        /* Обмеження робочих меж */
        if (new_pos < enc->min_position) {
            new_pos = enc->min_position;
        } else if (new_pos > enc->max_position) {
            new_pos = enc->max_position;
        }

        if (new_pos != enc->position) {
            enc->position = new_pos;
            return true;
        }
    }

    return false;
}

uint16_t encoder_to_pulse_us(const encoder_state_t *enc)
{
    if (enc == NULL) {
        return SERVO_PULSE_CENTER_US;
    }

    int32_t calculated_pulse = SERVO_PULSE_MIN_US + (enc->position * (int32_t)enc->pulse_step_us);
    
    if (calculated_pulse < (int32_t)SERVO_PULSE_MIN_US) {
        return SERVO_PULSE_MIN_US;
    }
    if (calculated_pulse > (int32_t)SERVO_PULSE_MAX_US) {
        return SERVO_PULSE_MAX_US;
    }

    return (uint16_t)calculated_pulse;
}

float encoder_to_angle_deg(const encoder_state_t *enc)
{
    uint16_t pulse = encoder_to_pulse_us(enc);
    float angle = ((float)(pulse - SERVO_PULSE_MIN_US) /
                  (float)(SERVO_PULSE_MAX_US - SERVO_PULSE_MIN_US)) * SERVO_ANGLE_MAX_DEG;
    return angle;
}

void encoder_set_position(encoder_state_t *enc, int32_t pos)
{
    if (enc == NULL) {
        return;
    }

    if (pos < enc->min_position) {
        pos = enc->min_position;
    } else if (pos > enc->max_position) {
        pos = enc->max_position;
    }

    enc->position = pos;
}
