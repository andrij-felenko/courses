#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

typedef enum {
    UART_OVERSAMPLING_16X = 16,
    UART_OVERSAMPLING_8X  = 8
} uart_os_mode_t;

typedef enum {
    RX_STATE_IDLE = 0,
    RX_STATE_START_VERIFY,
    RX_STATE_DATA_BITS,
    RX_STATE_STOP_VERIFY
} uart_rx_state_t;

typedef struct {
    uint8_t data_byte;
    bool    noise_flag;      /* Ознака шуму на лінії (вибірки 2:1) */
    bool    framing_error;   /* Помилка стоп-біта (стоп прочитано як 0) */
    bool    glitch_detected; /* Виявлено хибний старт */
} uart_rx_frame_t;

typedef struct {
    uart_os_mode_t   os_mode;
    uart_rx_state_t  state;
    uint8_t          subtick_counter;
    uint8_t          bit_index;
    uint8_t          shift_register;
    uint8_t          sample_buffer[3];
    uint8_t          prev_rx_pin;
    bool             frame_noise_accumulated;
    uart_rx_frame_t  last_frame;
    bool             has_new_frame;
} uart_rx_engine_t;

void uart_rx_init(uart_rx_engine_t *rx, uart_os_mode_t mode) {
    rx->os_mode = mode;
    rx->state = RX_STATE_IDLE;
    rx->subtick_counter = 0;
    rx->bit_index = 0;
    rx->shift_register = 0;
    rx->sample_buffer[0] = 1;
    rx->sample_buffer[1] = 1;
    rx->sample_buffer[2] = 1;
    rx->prev_rx_pin = 1;
    rx->frame_noise_accumulated = false;
    rx->has_new_frame = false;
    rx->last_frame.glitch_detected = false;
    rx->last_frame.framing_error = false;
    rx->last_frame.noise_flag = false;
    rx->last_frame.data_byte = 0;
}

/* Мажоритарне голосування 2 з 3 та детектор розбіжності */
static inline uint8_t majority_vote_3(const uint8_t s[3], bool *out_noise) {
    uint8_t sum = s[0] + s[1] + s[2];
    /* Якщо сума 1 або 2 — була розбіжність (шум на лінії) */
    *out_noise = (sum == 1 || sum == 2);
    return (sum >= 2) ? 1 : 0;
}

/* Обчислення позицій 3 центральних вибірок для обраного режиму */
static inline bool is_sample_subtick(uart_os_mode_t mode, uint8_t tick, uint8_t *sample_idx) {
    if (mode == UART_OVERSAMPLING_16X) {
        if (tick == 7)  { *sample_idx = 0; return true; }
        if (tick == 8)  { *sample_idx = 1; return true; }
        if (tick == 9)  { *sample_idx = 2; return true; }
    } else { /* 8X */
        if (tick == 3)  { *sample_idx = 0; return true; }
        if (tick == 4)  { *sample_idx = 1; return true; }
        if (tick == 5)  { *sample_idx = 2; return true; }
    }
    return false;
}

/* Такт апаратного автомата передискретизації */
void uart_rx_tick(uart_rx_engine_t *rx, uint8_t rx_pin) {
    uint8_t sample_idx = 0;
    const uint8_t last_tick = (uint8_t)rx->os_mode - 1;
    const uint8_t voting_tick = (rx->os_mode == UART_OVERSAMPLING_16X) ? 9 : 5;

    switch (rx->state) {
    case RX_STATE_IDLE:
        /* Детекція спадного фронту: лінія була 1 і стала 0 */
        if (rx->prev_rx_pin == 1 && rx_pin == 0) {
            rx->state = RX_STATE_START_VERIFY;
            rx->subtick_counter = 0;
            rx->frame_noise_accumulated = false;
        }
        break;

    case RX_STATE_START_VERIFY:
        /* Фіксація вибірок середини стартового біта */
        if (is_sample_subtick(rx->os_mode, rx->subtick_counter, &sample_idx)) {
            rx->sample_buffer[sample_idx] = rx_pin;
        }

        /* У момент останньої вибірки перевіряємо дійсність старту */
        if (rx->subtick_counter == voting_tick) {
            bool start_noise = false;
            uint8_t start_val = majority_vote_3(rx->sample_buffer, &start_noise);
            if (start_val != 0) {
                /* Хибний старт (завада / Glitch): лінія повернулася в 1 */
                rx->last_frame.glitch_detected = true;
                rx->state = RX_STATE_IDLE;
                break;
            }
            if (start_noise) {
                rx->frame_noise_accumulated = true;
            }
        }

        /* Завершення бітового інтервалу стартового біта */
        if (rx->subtick_counter >= last_tick) {
            rx->subtick_counter = 0;
            rx->bit_index = 0;
            rx->shift_register = 0;
            rx->state = RX_STATE_DATA_BITS;
        } else {
            rx->subtick_counter++;
        }
        break;

    case RX_STATE_DATA_BITS:
        if (is_sample_subtick(rx->os_mode, rx->subtick_counter, &sample_idx)) {
            rx->sample_buffer[sample_idx] = rx_pin;
        }

        /* Голосування наприкінці центрального вікна */
        if (rx->subtick_counter == voting_tick) {
            bool bit_noise = false;
            uint8_t bit_val = majority_vote_3(rx->sample_buffer, &bit_noise);
            if (bit_noise) {
                rx->frame_noise_accumulated = true;
            }
            /* Зсув даних молодшим бітом уперед (LSB First) */
            rx->shift_register |= (bit_val << rx->bit_index);
        }

        if (rx->subtick_counter >= last_tick) {
            rx->subtick_counter = 0;
            rx->bit_index++;
            if (rx->bit_index >= 8) {
                rx->state = RX_STATE_STOP_VERIFY;
            }
        } else {
            rx->subtick_counter++;
        }
        break;

    case RX_STATE_STOP_VERIFY:
        if (is_sample_subtick(rx->os_mode, rx->subtick_counter, &sample_idx)) {
            rx->sample_buffer[sample_idx] = rx_pin;
        }

        if (rx->subtick_counter == voting_tick) {
            bool stop_noise = false;
            uint8_t stop_val = majority_vote_3(rx->sample_buffer, &stop_noise);
            if (stop_noise) {
                rx->frame_noise_accumulated = true;
            }

            /* Формування вихідного кадру */
            rx->last_frame.data_byte = rx->shift_register;
            rx->last_frame.noise_flag = rx->frame_noise_accumulated;
            rx->last_frame.framing_error = (stop_val == 0); /* Стоп має бути 1 */
            rx->last_frame.glitch_detected = false;
            rx->has_new_frame = true;
        }

        if (rx->subtick_counter >= last_tick) {
            rx->subtick_counter = 0;
            rx->state = RX_STATE_IDLE;
        } else {
            rx->subtick_counter++;
        }
        break;
    }

    rx->prev_rx_pin = rx_pin;
}
