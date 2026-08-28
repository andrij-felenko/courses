#include <stdint.h>
#include <stdbool.h>

/* Структура одного блоку SACK у пам'яті (відповідає struct tcp_sack_block у Linux) */
typedef struct {
    uint32_t start_seq; /* Ліва межа блоку: перший отриманий байт */
    uint32_t end_seq;   /* Права межа блоку: перший байт ПІСЛЯ блоку */
} TcpSackBlock;

/* Стан вибіркових підтверджень сокета TCP */
#define TCP_NUM_SACKS 4

typedef struct {
    uint8_t      num_sacks;                    /* Кількість дійсних блоків (0..4) */
    TcpSackBlock selective_acks[TCP_NUM_SACKS]; /* Масив блоків SACK */
    uint32_t     cumulative_ack;               /* Кумулятивний ACK */
    bool         dsack_detected;               /* Ознака наявності D-SACK */
} TcpSackState;

/* Парсер опцій SACK із сирого буфера TCP */
bool parse_tcp_sack_option(const uint8_t *opt_ptr, uint8_t opt_len, TcpSackState *state) {
    if (opt_len < 10 || ((opt_len - 2) % 8) != 0) {
        return false; /* Некоректна довжина опції SACK */
    }

    uint8_t num_blocks = (uint8_t)((opt_len - 2) / 8);
    if (num_blocks > TCP_NUM_SACKS) num_blocks = TCP_NUM_SACKS;

    state->num_sacks = num_blocks;
    const uint8_t *p = opt_ptr + 2; /* Пропускаємо Kind та Length */

    for (uint8_t i = 0; i < num_blocks; ++i) {
        /* Зчитування 32-бітових чисел у мережевому порядку байтів (Big-Endian) */
        uint32_t left = ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
                        ((uint32_t)p[2] << 8)  | (uint32_t)p[3];
        uint32_t right = ((uint32_t)p[4] << 24) | ((uint32_t)p[5] << 16) |
                         ((uint32_t)p[6] << 8)  | (uint32_t)p[7];

        state->selective_acks[i].start_seq = left;
        state->selective_acks[i].end_seq = right;
        p += 8;
    }

    /* Перевірка на Duplicate SACK (D-SACK за RFC 2883) */
    if (num_blocks > 0) {
        uint32_t first_left = state->selective_acks[0].start_seq;
        uint32_t first_right = state->selective_acks[0].end_seq;
        if (first_left < state->cumulative_ack ||
           (num_blocks > 1 && first_left >= state->selective_acks[1].start_seq &&
            first_right <= state->selective_acks[1].end_seq)) {
            state->dsack_detected = true;
        } else {
            state->dsack_detected = false;
        }
    }
    return true;
}
