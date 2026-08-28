#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

#define MAX_PAYLOAD  64
#define SEQ_SPACE    8   /* Простір номерів M = 8 (номери від 0 до 7) */
#define WIN_SIZE_GBN 4   /* Розмір вікна GBN: W <= M - 1 */
#define WIN_SIZE_SR  4   /* Розмір вікна SR: W <= M / 2 */
#define RTO_TICKS    5   /* Таймаут повторної передачі в тактах */

typedef enum {
    FRAME_DATA = 1,
    FRAME_ACK  = 2,
    FRAME_NACK = 3
} FrameType;

typedef struct {
    uint8_t   type;
    uint8_t   seq;
    uint8_t   ack;
    uint8_t   len;
    uint8_t   payload[MAX_PAYLOAD];
    uint16_t  crc;
} Frame;

/* Обчислення контрольної суми CRC16-CCITT над полями кадру */
static uint16_t calc_crc16(const Frame *f) {
    uint16_t crc = 0xFFFF;
    const uint8_t *data = (const uint8_t *)f;
    size_t len = sizeof(Frame) - sizeof(uint16_t);
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000) crc = (crc << 1) ^ 0x1021;
            else crc <<= 1;
        }
    }
    return crc;
}

/* Модульна перевірка: чи потрапляє номер seq у вікно [base .. base + win - 1] */
static bool is_in_window(uint8_t seq, uint8_t base, uint8_t win) {
    uint8_t dist = (uint8_t)((seq - base + SEQ_SPACE) % SEQ_SPACE);
    return dist < win;
}

/* ── Стан передавача Go-Back-N ── */
typedef struct {
    uint8_t send_base;
    uint8_t next_seq;
    Frame   buffer[SEQ_SPACE];
    int     timer_ticks;
    bool    timer_running;
} GbnSender;

/* ── Стан приймача Go-Back-N ── */
typedef struct {
    uint8_t expected_seq;
} GbnReceiver;

void gbn_sender_init(GbnSender *s) {
    s->send_base = 0;
    s->next_seq = 0;
    s->timer_ticks = 0;
    s->timer_running = false;
}

void gbn_receiver_init(GbnReceiver *r) {
    r->expected_seq = 0;
}

/* Відправлення нового кадру даних через Go-Back-N */
bool gbn_sender_send(GbnSender *s, const uint8_t *data, uint8_t len, Frame *out_frame) {
    if (!is_in_window(s->next_seq, s->send_base, WIN_SIZE_GBN)) {
        return false; /* Вікно заповнене, передачу заблоковано */
    }

    Frame *f = &s->buffer[s->next_seq];
    f->type = FRAME_DATA;
    f->seq = s->next_seq;
    f->ack = 0;
    f->len = len;
    memcpy(f->payload, data, len);
    f->crc = calc_crc16(f);

    *out_frame = *f;
    s->next_seq = (s->next_seq + 1) % SEQ_SPACE;

    if (!s->timer_running) {
        s->timer_running = true;
        s->timer_ticks = RTO_TICKS;
    }
    return true;
}

/* Обробка отриманого кадру на приймачі Go-Back-N */
bool gbn_receiver_on_frame(GbnReceiver *r, const Frame *in, Frame *out_ack) {
    if (calc_crc16(in) != in->crc) {
        return false; /* Спотворений кадр відкидаємо без відповіді */
    }

    if (in->type == FRAME_DATA && in->seq == r->expected_seq) {
        /* Кадр надійшов у суворій послідовності */
        r->expected_seq = (r->expected_seq + 1) % SEQ_SPACE;

        out_ack->type = FRAME_ACK;
        out_ack->seq = 0;
        out_ack->ack = r->expected_seq; /* Кумулятивне підтвердження: чекаємо наступний */
        out_ack->len = 0;
        out_ack->crc = calc_crc16(out_ack);
        return true;
    }

    /* Позачерговий або дубльований кадр відкидаємо, повторюємо останній дійсний ACK */
    out_ack->type = FRAME_ACK;
    out_ack->seq = 0;
    out_ack->ack = r->expected_seq;
    out_ack->len = 0;
    out_ack->crc = calc_crc16(out_ack);
    return true;
}

/* Обробка отриманого підтвердження на передавачі Go-Back-N */
void gbn_sender_on_ack(GbnSender *s, const Frame *ack) {
    if (calc_crc16(ack) != ack->crc || ack->type != FRAME_ACK) return;

    /* Перевіряємо, чи просуває отриманий ack базу вікна вперед */
    if (is_in_window(ack->ack, s->send_base, WIN_SIZE_GBN + 1)) {
        s->send_base = ack->ack;
        if (s->send_base == s->next_seq) {
            s->timer_running = false; /* Усі відправлені кадри підтверджено */
        } else {
            s->timer_ticks = RTO_TICKS; /* Перезапуск таймера для наступного непідтвердженого */
        }
    }
}

/* Обробка такту таймера на передавачі Go-Back-N */
int gbn_sender_tick(GbnSender *s, Frame retransmit_queue[]) {
    if (!s->timer_running) return 0;

    s->timer_ticks--;
    if (s->timer_ticks > 0) return 0;

    /* Спрацював таймаут RTO -> Go Back N: повторюємо ВСІ неподтверджені кадри */
    s->timer_ticks = RTO_TICKS;
    int count = 0;
    uint8_t curr = s->send_base;
    while (curr != s->next_seq) {
        retransmit_queue[count++] = s->buffer[curr];
        curr = (curr + 1) % SEQ_SPACE;
    }
    return count;
}
