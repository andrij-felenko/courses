#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ARQ_MAX_PAYLOAD 64
#define ARQ_MAX_RETRIES 5
#define ARQ_MIN_RTO_MS  20
#define ARQ_MAX_RTO_MS  2000
#define ARQ_INITIAL_RTO 100

typedef enum {
    FRAME_DATA = 0x01,
    FRAME_ACK  = 0x02,
    FRAME_NACK = 0x03
} FrameType;

typedef struct {
    uint8_t   type;
    uint8_t   seq;
    uint8_t   len;
    uint8_t   payload[ARQ_MAX_PAYLOAD];
    uint16_t  crc;
} __attribute__((packed)) ArqFrame;

typedef enum {
    TX_STATE_IDLE,
    TX_STATE_WAIT_ACK,
    TX_STATE_FAILED
} TxState;

typedef struct {
    TxState   state;
    uint8_t   next_seq;
    uint8_t   retries;
    uint32_t  tx_timestamp;
    bool      is_retransmission;
    ArqFrame  pending_frame;

    /* Параметри цілочисельного RTO Якобсона/Карна */
    uint32_t  srtt_scaled;    /* SRTT * 8 */
    uint32_t  rttvar_scaled;  /* RTTVAR * 4 */
    uint32_t  rto_ms;
} ArqSender;

typedef struct {
    uint8_t   expected_seq;
} ArqReceiver;

/* Спрощений розрахунок CRC16 CCITT */
static uint16_t arq_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t b = 0; b < 8; ++b) {
            if (crc & 0x8000) crc = (crc << 1) ^ 0x1021;
            else              crc = crc << 1;
        }
    }
    return crc;
}

/* Ініціалізація передавача */
void arq_sender_init(ArqSender *s) {
    s->state = TX_STATE_IDLE;
    s->next_seq = 0;
    s->retries = 0;
    s->is_retransmission = false;
    s->srtt_scaled = ARQ_INITIAL_RTO << 3;
    s->rttvar_scaled = (ARQ_INITIAL_RTO / 2) << 2;
    s->rto_ms = ARQ_INITIAL_RTO;
}

/* Оновлення RTO за Якобсоном (тільки для неперепосланих пакетів) */
static void arq_update_rtt(ArqSender *s, uint32_t sample_rtt_ms) {
    int32_t err = (int32_t)sample_rtt_ms - (int32_t)(s->srtt_scaled >> 3);
    s->srtt_scaled += err;
    
    int32_t abs_err = (err < 0) ? -err : err;
    s->rttvar_scaled += abs_err - (int32_t)(s->rttvar_scaled >> 2);
    
    s->rto_ms = (s->srtt_scaled >> 3) + s->rttvar_scaled;
    if (s->rto_ms < ARQ_MIN_RTO_MS) s->rto_ms = ARQ_MIN_RTO_MS;
    if (s->rto_ms > ARQ_MAX_RTO_MS) s->rto_ms = ARQ_MAX_RTO_MS;
}

/* Відправка даних (виклик від додатку) */
bool arq_send(ArqSender *s, const uint8_t *data, uint8_t len, uint32_t now_ms,
              void (*hw_transmit)(const uint8_t *buf, size_t size)) {
    if (s->state != TX_STATE_IDLE || len > ARQ_MAX_PAYLOAD) {
        return false;
    }

    s->pending_frame.type = FRAME_DATA;
    s->pending_frame.seq = s->next_seq;
    s->pending_frame.len = len;
    memcpy(s->pending_frame.payload, data, len);

    size_t header_len = sizeof(ArqFrame) - sizeof(uint16_t);
    s->pending_frame.crc = arq_crc16((uint8_t *)&s->pending_frame, header_len);

    s->tx_timestamp = now_ms;
    s->retries = 0;
    s->is_retransmission = false;
    s->state = TX_STATE_WAIT_ACK;

    hw_transmit((const uint8_t *)&s->pending_frame, sizeof(ArqFrame));
    return true;
}

/* Періодичний тік передавача: перевірка таймауту */
void arq_sender_poll(ArqSender *s, uint32_t now_ms,
                     void (*hw_transmit)(const uint8_t *buf, size_t size)) {
    if (s->state != TX_STATE_WAIT_ACK) return;

    if (now_ms - s->tx_timestamp >= s->rto_ms) {
        if (s->retries < ARQ_MAX_RETRIES) {
            s->retries++;
            s->is_retransmission = true;
            s->rto_ms = (s->rto_ms * 2 > ARQ_MAX_RTO_MS) ? ARQ_MAX_RTO_MS : s->rto_ms * 2;
            s->tx_timestamp = now_ms;
            hw_transmit((const uint8_t *)&s->pending_frame, sizeof(ArqFrame));
        } else {
            s->state = TX_STATE_FAILED;
        }
    }
}

/* Обробка вхідного кадру квитанції */
void arq_sender_on_ack_received(ArqSender *s, const ArqFrame *ack, uint32_t now_ms) {
    if (s->state != TX_STATE_WAIT_ACK) return;

    size_t header_len = sizeof(ArqFrame) - sizeof(uint16_t);
    if (arq_crc16((const uint8_t *)ack, header_len) != ack->crc) return;

    if (ack->type == FRAME_ACK && ack->seq == s->next_seq) {
        if (!s->is_retransmission) {
            uint32_t sample_rtt = now_ms - s->tx_timestamp;
            arq_update_rtt(s, sample_rtt);
        }
        s->next_seq ^= 1; /* 1-бітне чергування в Stop-and-Wait */
        s->state = TX_STATE_IDLE;
    }
}

/* Обробка на боці приймача */
void arq_receiver_init(ArqReceiver *r) {
    r->expected_seq = 0;
}

void arq_receiver_on_frame(ArqReceiver *r, const ArqFrame *frame,
                           void (*hw_transmit)(const uint8_t *buf, size_t size),
                           void (*app_deliver)(const uint8_t *data, uint8_t len)) {
    size_t header_len = sizeof(ArqFrame) - sizeof(uint16_t);
    if (arq_crc16((const uint8_t *)frame, header_len) != frame->crc) {
        return; /* Помилка CRC: відкидаємо сміття */
    }

    if (frame->type == FRAME_DATA) {
        ArqFrame ack_reply;
        ack_reply.type = FRAME_ACK;
        ack_reply.seq = frame->seq;
        ack_reply.len = 0;
        ack_reply.crc = arq_crc16((uint8_t *)&ack_reply, header_len);

        if (frame->seq == r->expected_seq) {
            /* Свіжі дані: віддаємо додатку та зсуваємо чергу */
            app_deliver(frame->payload, frame->len);
            r->expected_seq ^= 1;
        }
        /* У будь-якому випадку (свіжий чи дублікат) надсилаємо ACK */
        hw_transmit((const uint8_t *)&ack_reply, sizeof(ArqFrame));
    }
}
