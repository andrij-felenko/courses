#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define SLIP_END     0xC0
#define SLIP_ESC     0xDB
#define SLIP_ESC_END 0xDC
#define SLIP_ESC_ESC 0xDD

/* Стани кінцевого автомата декодера */
typedef enum {
    SLIP_STATE_NORMAL = 0,
    SLIP_STATE_ESCAPED
} slip_state_t;

/* Контекст потокового декодера SLIP */
typedef struct slip_decoder {
    uint8_t *rx_buffer;
    size_t   max_length;
    size_t   current_length;
    slip_state_t state;
    bool     overflow_flag;
    void   (*on_packet_received)(const uint8_t *data, size_t length, void *user_data);
    void    *user_data;
} slip_decoder_t;

/* Ініціалізація декодера */
void slip_decoder_init(slip_decoder_t *dec, uint8_t *buffer, size_t max_len,
                       void (*callback)(const uint8_t *, size_t, void *), void *user_data) {
    dec->rx_buffer = buffer;
    dec->max_length = max_len;
    dec->current_length = 0;
    dec->state = SLIP_STATE_NORMAL;
    dec->overflow_flag = false;
    dec->on_packet_received = callback;
    dec->user_data = user_data;
}

/* Скидання стану декодера після помилки або розриву з'єднання */
void slip_decoder_reset(slip_decoder_t *dec) {
    dec->current_length = 0;
    dec->state = SLIP_STATE_NORMAL;
    dec->overflow_flag = false;
}

/* Потокова обробка одного отриманого байта */
void slip_decoder_feed_byte(slip_decoder_t *dec, uint8_t byte) {
    switch (dec->state) {
    case SLIP_STATE_NORMAL:
        if (byte == SLIP_END) {
            /* Кінець пакета: якщо довжина > 0 і не було переповнення, викликаємо callback */
            if (dec->current_length > 0) {
                if (!dec->overflow_flag && dec->on_packet_received) {
                    dec->on_packet_received(dec->rx_buffer, dec->current_length, dec->user_data);
                }
                dec->current_length = 0;
                dec->overflow_flag = false;
            }
        } else if (byte == SLIP_ESC) {
            dec->state = SLIP_STATE_ESCAPED;
        } else {
            /* Звичайний байт даних */
            if (dec->current_length < dec->max_length) {
                dec->rx_buffer[dec->current_length++] = byte;
            } else {
                dec->overflow_flag = true; /* Переповнення MTU */
            }
        }
        break;

    case SLIP_STATE_ESCAPED:
        if (byte == SLIP_ESC_END) {
            if (dec->current_length < dec->max_length) {
                dec->rx_buffer[dec->current_length++] = SLIP_END;
            } else {
                dec->overflow_flag = true;
            }
            dec->state = SLIP_STATE_NORMAL;
        } else if (byte == SLIP_ESC_ESC) {
            if (dec->current_length < dec->max_length) {
                dec->rx_buffer[dec->current_length++] = SLIP_ESC;
            } else {
                dec->overflow_flag = true;
            }
            dec->state = SLIP_STATE_NORMAL;
        } else if (byte == SLIP_END) {
            /* Порушення протоколу: неочікуваний END одразу після ESC */
            dec->current_length = 0;
            dec->overflow_flag = false;
            dec->state = SLIP_STATE_NORMAL;
        } else {
            /* Невідомий символ після ESC за RFC 1055 додається як є */
            if (dec->current_length < dec->max_length) {
                dec->rx_buffer[dec->current_length++] = byte;
            } else {
                dec->overflow_flag = true;
            }
            dec->state = SLIP_STATE_NORMAL;
        }
        break;
    }
}

/* Кодування пакета в вихідний буфер. Повертає кількість записаних байтів або 0 при нестачі місця */
size_t slip_encode_frame(const uint8_t *src, size_t src_len, uint8_t *dst, size_t dst_max_len) {
    size_t out_pos = 0;

    /* Початковий END для очищення можливих шумів лінії перед початком кадру */
    if (out_pos >= dst_max_len) return 0;
    dst[out_pos++] = SLIP_END;

    for (size_t i = 0; i < src_len; ++i) {
        uint8_t b = src[i];
        if (b == SLIP_END) {
            if (out_pos + 2 > dst_max_len) return 0;
            dst[out_pos++] = SLIP_ESC;
            dst[out_pos++] = SLIP_ESC_END;
        } else if (b == SLIP_ESC) {
            if (out_pos + 2 > dst_max_len) return 0;
            dst[out_pos++] = SLIP_ESC;
            dst[out_pos++] = SLIP_ESC_ESC;
        } else {
            if (out_pos + 1 > dst_max_len) return 0;
            dst[out_pos++] = b;
        }
    }

    /* Кінцевий маркер END */
    if (out_pos >= dst_max_len) return 0;
    dst[out_pos++] = SLIP_END;

    return out_pos;
}
