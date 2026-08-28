/* c — Повний C-драйвер декодера NEC-протоколу з кінцевим автоматом */
#include <stdint.h>
#include <stdbool.h>

/* Структура декодованого кадру NEC */
typedef struct {
    uint32_t raw_code;     /* Повний 32-бітний код кадру */
    uint8_t  address;      /* 8-бітний адрес пристрою */
    uint8_t  address_inv;  /* Інверсний адрес для перевірки паритету */
    uint8_t  command;      /* 8-бітна команда */
    uint8_t  command_inv;  /* Інверсна команда */
    bool     is_repeat;    /* Прапорець кадру повтору */
    bool     valid;        /* Прапорець успішної перевірки КС */
} nec_frame_t;

/* Стани кінцевого автомата декодера */
typedef enum {
    NEC_STATE_IDLE,
    NEC_STATE_HEADER_SPACE,
    NEC_STATE_BIT_PULSE,
    NEC_STATE_BIT_SPACE
} nec_rx_state_t;

static nec_rx_state_t g_rx_state = NEC_STATE_IDLE;
static uint32_t g_rx_shift_reg = 0;
static uint8_t  g_rx_bit_count = 0;
static nec_frame_t g_last_frame = {0};

/*
 * Обробник переривання по зміні рівня виводу (Input Capture ISR).
 * delta_us — тривалість попереднього стану у мікросекундах.
 * pin_state_low — true, якщо поточний рівень на вході LOW (пачка 38 кГц).
 */
void nec_rx_process_edge(uint32_t delta_us, bool pin_state_low) {
    switch (g_rx_state) {
        case NEC_STATE_IDLE:
            /* Очікуємо спад сигналу: пачка преамбули тривалістю ~9000 мкс */
            if (pin_state_low && delta_us >= 8000 && delta_us <= 10000) {
                g_rx_state = NEC_STATE_HEADER_SPACE;
            }
            break;

        case NEC_STATE_HEADER_SPACE:
            /* Очікуємо паузу преамбули: 4500 мкс (звичайний кадр) або 2250 мкс (повтор) */
            if (!pin_state_low) {
                if (delta_us >= 4000 && delta_us <= 5000) {
                    g_rx_shift_reg = 0;
                    g_rx_bit_count = 0;
                    g_rx_state = NEC_STATE_BIT_PULSE;
                } else if (delta_us >= 2000 && delta_us <= 2600) {
                    /* Зафіксовано повтор натискання кнопки */
                    g_last_frame.is_repeat = true;
                    g_last_frame.valid = true;
                    g_rx_state = NEC_STATE_IDLE;
                } else {
                    g_rx_state = NEC_STATE_IDLE;
                }
            }
            break;

        case NEC_STATE_BIT_PULSE:
            /* Пачка перед кожним бітом: ~562 мкс */
            if (pin_state_low && delta_us >= 400 && delta_us <= 750) {
                g_rx_state = NEC_STATE_BIT_SPACE;
            } else {
                g_rx_state = NEC_STATE_IDLE;
            }
            break;

        case NEC_STATE_BIT_SPACE:
            /* Пауза визначає біт: ~562 мкс -> '0', ~1687 мкс -> '1' */
            if (!pin_state_low) {
                g_rx_shift_reg >>= 1;
                if (delta_us >= 1400 && delta_us <= 1950) {
                    g_rx_shift_reg |= 0x80000000UL; /* Біт '1' */
                } else if (delta_us < 400 || delta_us > 850) {
                    g_rx_state = NEC_STATE_IDLE;    /* Помилка таймингу */
                    break;
                }

                g_rx_bit_count++;
                if (g_rx_bit_count >= 32) {
                    /* Прийнято всі 32 біти: перевіряємо контрольні байти */
                    uint8_t addr  = (g_rx_shift_reg >> 0)  & 0xFF;
                    uint8_t naddr = (g_rx_shift_reg >> 8)  & 0xFF;
                    uint8_t cmd   = (g_rx_shift_reg >> 16) & 0xFF;
                    uint8_t ncmd  = (g_rx_shift_reg >> 24) & 0xFF;

                    if ((addr ^ naddr) == 0xFF && (cmd ^ ncmd) == 0xFF) {
                        g_last_frame.raw_code    = g_rx_shift_reg;
                        g_last_frame.address     = addr;
                        g_last_frame.address_inv = naddr;
                        g_last_frame.command     = cmd;
                        g_last_frame.command_inv = ncmd;
                        g_last_frame.is_repeat   = false;
                        g_last_frame.valid       = true;
                    }
                    g_rx_state = NEC_STATE_IDLE;
                } else {
                    g_rx_state = NEC_STATE_BIT_PULSE;
                }
            }
            break;
    }
}

bool nec_get_frame(nec_frame_t *out_frame) {
    if (g_last_frame.valid) {
        *out_frame = g_last_frame;
        g_last_frame.valid = false;
        return true;
    }
    return false;
}
