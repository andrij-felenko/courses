/* arq.h — Stop-and-Wait ARQ поверх уже кадрованої лінії.
 *
 * Один заголовок на всю навчальну бібліотеку: формат кадру, оцінювач RTO
 * (Якобсон + Карн), автомат передавача й автомат приймача.
 *
 * Кадр на лінії:
 *   SOF | TYPE | SEQ | LEN | PAYLOAD[LEN] | CRC16 (little-endian)
 * CRC рахується від TYPE до останнього байта корисних даних.
 * Межі кадру дає нижній рівень кадрування (COBS/SLIP); SOF лишається
 * дешевою перевіркою синхронізації перед розбором.
 */
#ifndef ARQ_H
#define ARQ_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define ARQ_SOF         0x7Eu
#define ARQ_MAX_PAYLOAD 64u
#define ARQ_HDR_LEN     4u /* SOF + TYPE + SEQ + LEN */
#define ARQ_CRC_LEN     2u
#define ARQ_MAX_FRAME   (ARQ_HDR_LEN + ARQ_MAX_PAYLOAD + ARQ_CRC_LEN)

/* Параметри протоколу. RTO стартує зі 100 мс і далі живе за виміром. */
#define ARQ_MAX_RETRIES    5u
#define ARQ_MIN_RTO_MS     20u
#define ARQ_MAX_RTO_MS     2000u
#define ARQ_INITIAL_RTO_MS 100u

enum arq_type {
    ARQ_DATA = 0x01,
    ARQ_ACK  = 0x02,
    ARQ_NACK = 0x03
};

typedef struct {
    uint8_t type;
    uint8_t seq; /* 1-бітний чергований номер: тільки 0 або 1 */
    uint8_t len;
    uint8_t payload[ARQ_MAX_PAYLOAD];
} arq_frame;

typedef enum {
    ARQ_DEC_OK = 0,
    ARQ_DEC_TOO_SHORT,
    ARQ_DEC_NO_SOF,
    ARQ_DEC_BAD_LEN,
    ARQ_DEC_BAD_TYPE,
    ARQ_DEC_BAD_SEQ,
    ARQ_DEC_BAD_CRC
} arq_decode_res;

/* --- Кодек кадру (frame.c) --- */
uint16_t       arq_crc16(const uint8_t *data, size_t len);
size_t         arq_encode(const arq_frame *f, uint8_t *out, size_t out_cap); /* 0 = не влізло */
arq_decode_res arq_decode(const uint8_t *wire, size_t len, arq_frame *out);
const char    *arq_decode_str(arq_decode_res res);

/* --- Оцінювач таймауту (rto.c) ---
 * Цілочисельна фіксована кома: srtt_scaled = SRTT·8, rttvar_scaled = RTTVAR·4.
 */
typedef struct {
    uint32_t srtt_scaled;
    uint32_t rttvar_scaled;
    uint32_t rto_ms;
    bool     has_sample;
} arq_rto;

void     arq_rto_init(arq_rto *e);
void     arq_rto_update(arq_rto *e, uint32_t sample_ms); /* Карн №1: лише кадр без повторів */
void     arq_rto_backoff(arq_rto *e);                    /* Карн №2: подвоєння на таймауті */
uint32_t arq_rto_get(const arq_rto *e);
uint32_t arq_rto_srtt(const arq_rto *e);

/* --- Зв'язок із зовнішнім світом --- */
typedef void (*arq_write_fn)(void *ctx, const uint8_t *frame, size_t len);
typedef void (*arq_result_fn)(void *ctx, bool delivered, uint8_t seq);
typedef void (*arq_deliver_fn)(void *ctx, const uint8_t *data, uint8_t len);

/* --- Передавач (arq_tx.c) --- */
typedef enum {
    ARQ_TX_IDLE,
    ARQ_TX_WAIT_ACK,
    ARQ_TX_FAILED
} arq_tx_state;

typedef struct {
    uint32_t sent;          /* нових кадрів віддано в лінію */
    uint32_t retransmitted; /* повторів (таймаут або NACK) */
    uint32_t acked;
    uint32_t failed;        /* здалися після ARQ_MAX_RETRIES */
    uint32_t stray;         /* биті або чужі квитанції */
} arq_tx_stats;

typedef struct {
    arq_tx_state state;
    uint8_t      seq;      /* номер кадру, що зараз у польоті */
    uint8_t      retries;
    uint32_t     sent_at_ms;
    bool         retransmitted; /* прапорець Карна для поточного кадру */

    uint8_t wire[ARQ_MAX_FRAME]; /* копія кадру для повтору */
    size_t  wire_len;

    arq_rto       rto;
    arq_write_fn  write;
    void         *write_ctx;
    arq_result_fn on_result;
    void         *result_ctx;
    arq_tx_stats  stats;
} arq_tx;

void arq_tx_init(arq_tx *tx, arq_write_fn write, void *write_ctx,
                 arq_result_fn on_result, void *result_ctx);
bool arq_tx_send(arq_tx *tx, const uint8_t *data, uint8_t len, uint32_t now_ms);
void arq_tx_poll(arq_tx *tx, uint32_t now_ms);
void arq_tx_on_wire(arq_tx *tx, const uint8_t *wire, size_t len, uint32_t now_ms);

/* --- Приймач (arq_rx.c) --- */
typedef struct {
    uint32_t delivered;
    uint32_t duplicates;
    uint32_t corrupted;
    uint32_t ignored;
} arq_rx_stats;

typedef struct {
    uint8_t        expected_seq;
    arq_decode_res last_error;
    arq_write_fn   write;
    void          *write_ctx;
    arq_deliver_fn deliver;
    void          *deliver_ctx;
    arq_rx_stats   stats;
} arq_rx;

void arq_rx_init(arq_rx *rx, arq_write_fn write, void *write_ctx,
                 arq_deliver_fn deliver, void *deliver_ctx);
void arq_rx_on_wire(arq_rx *rx, const uint8_t *wire, size_t len);

#endif /* ARQ_H */
