#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_WINDOW_SIZE  16
#define SEQ_SPACE        32   /* M = 2^5 = 32, W <= 16 для SR */
#define PAYLOAD_SIZE     32
#define MAX_EVENTS       128

typedef enum {
    FRAME_DATA = 0,
    FRAME_ACK,
    FRAME_NACK
} FrameType;

typedef struct {
    FrameType type;
    uint8_t seq;
    uint8_t ack;
    uint8_t payload[PAYLOAD_SIZE];
    size_t length;
} Frame;

/* Кільцевий буфер передавача */
typedef struct {
    Frame frame;
    bool in_flight;
    bool acked;
    uint32_t sent_time;
    uint32_t timeout_time;
} TxSlot;

typedef struct {
    uint8_t window_size;
    uint8_t s_base;
    uint8_t s_next;
    uint32_t rto_ticks;
    TxSlot buffer[SEQ_SPACE];
} SenderGBN;

typedef struct {
    uint8_t r_expected;
    uint32_t packets_received;
} ReceiverGBN;

/* Обчислення модульної відстані на кільці */
static inline uint8_t mod_dist(uint8_t from, uint8_t to, uint8_t mod) {
    return (to - from + mod) % mod;
}

/* ─── Ініціалізація та методи Go-Back-N ─── */
void gbn_sender_init(SenderGBN *snd, uint8_t win_size, uint32_t rto) {
    snd->window_size = win_size;
    snd->s_base = 0;
    snd->s_next = 0;
    snd->rto_ticks = rto;
    memset(snd->buffer, 0, sizeof(snd->buffer));
}

bool gbn_sender_send(SenderGBN *snd, const uint8_t *data, size_t len, uint32_t current_time, Frame *out_frame) {
    uint8_t used = mod_dist(snd->s_base, snd->s_next, SEQ_SPACE);
    if (used >= snd->window_size) {
        return false; /* Вікно заповнене, передача неможлива */
    }

    uint8_t seq = snd->s_next;
    TxSlot *slot = &snd->buffer[seq];
    slot->frame.type = FRAME_DATA;
    slot->frame.seq = seq;
    slot->frame.ack = 0;
    slot->frame.length = len < PAYLOAD_SIZE ? len : PAYLOAD_SIZE;
    memcpy(slot->frame.payload, data, slot->frame.length);
    
    slot->in_flight = true;
    slot->acked = false;
    slot->sent_time = current_time;
    slot->timeout_time = current_time + snd->rto_ticks;

    *out_frame = slot->frame;
    snd->s_next = (snd->s_next + 1) % SEQ_SPACE;
    return true;
}

void gbn_sender_on_ack(SenderGBN *snd, uint8_t ack_seq) {
    /* Кумулятивний ACK: підтверджує всі кадри від s_base до ack_seq */
    uint8_t advance = mod_dist(snd->s_base, (ack_seq + 1) % SEQ_SPACE, SEQ_SPACE);
    uint8_t max_advance = mod_dist(snd->s_base, snd->s_next, SEQ_SPACE);

    if (advance > 0 && advance <= max_advance) {
        while (snd->s_base != (ack_seq + 1) % SEQ_SPACE) {
            snd->buffer[snd->s_base].in_flight = false;
            snd->buffer[snd->s_base].acked = true;
            snd->s_base = (snd->s_base + 1) % SEQ_SPACE;
        }
    }
}

int gbn_sender_check_timeouts(SenderGBN *snd, uint32_t current_time, Frame out_frames[], int max_out) {
    /* Якщо для s_base сплив таймаут — повторюємо ВСІ кадри від s_base до s_next */
    if (snd->s_base == snd->s_next) return 0;

    TxSlot *base_slot = &snd->buffer[snd->s_base];
    if (base_slot->in_flight && current_time >= base_slot->timeout_time) {
        int count = 0;
        uint8_t curr = snd->s_base;
        while (curr != snd->s_next && count < max_out) {
            snd->buffer[curr].sent_time = current_time;
            snd->buffer[curr].timeout_time = current_time + snd->rto_ticks;
            out_frames[count++] = snd->buffer[curr].frame;
            curr = (curr + 1) % SEQ_SPACE;
        }
        return count;
    }
    return 0;
}

/* ─── Приймач Go-Back-N ─── */
void gbn_receiver_init(ReceiverGBN *rcv) {
    rcv->r_expected = 0;
    rcv->packets_received = 0;
}

bool gbn_receiver_on_frame(ReceiverGBN *rcv, const Frame *f, Frame *out_ack) {
    if (f->type != FRAME_DATA) return false;

    if (f->seq == rcv->r_expected) {
        /* Отримано очікуваний кадр */
        rcv->packets_received++;
        out_ack->type = FRAME_ACK;
        out_ack->seq = 0;
        out_ack->ack = rcv->r_expected;
        out_ack->length = 0;
        rcv->r_expected = (rcv->r_expected + 1) % SEQ_SPACE;
        return true;
    } else {
        /* Невпорядкований кадр — відкидаємо, повторюємо старий ACK */
        if (rcv->packets_received > 0) {
            out_ack->type = FRAME_ACK;
            out_ack->seq = 0;
            out_ack->ack = (rcv->r_expected + SEQ_SPACE - 1) % SEQ_SPACE;
            out_ack->length = 0;
            return true;
        }
        return false;
    }
}

/* ─── Демонстраційний запуск симуляції ─── */
int main(void) {
    SenderGBN sender;
    ReceiverGBN receiver;
    gbn_sender_init(&sender, 4, 10); /* Вікно W = 4, RTO = 10 тіків */
    gbn_receiver_init(&receiver);

    printf("=== Симуляція протоколу Go-Back-N (C99) ===\n");
    for (int i = 0; i < 6; i++) {
        char msg[20];
        snprintf(msg, sizeof(msg), "DataBlock-%d", i);
        Frame f;
        if (gbn_sender_send(&sender, (uint8_t*)msg, strlen(msg), i * 2, &f)) {
            printf("[TX %u] Відправлено кадр Seq=%u (%s)\n", i * 2, f.seq, msg);
            
            /* Емуляція втрати кадру з Seq=1 */
            if (f.seq == 1) {
                printf("  [ВТРАТА] Кадр Seq=1 загубився в каналі зв'язку!\n");
                continue;
            }

            Frame ack;
            if (gbn_receiver_on_frame(&receiver, &f, &ack)) {
                printf("  [RX] Прийнято Seq=%u, надіслано ACK=%u\n", f.seq, ack.ack);
                gbn_sender_on_ack(&sender, ack.ack);
            }
        }
    }

    /* Симуляція спливання таймауту */
    printf("\n--- Спрацьовує таймаут RTO для кадру Seq=1 ---\n");
    Frame retrans[MAX_WINDOW_SIZE];
    int n = gbn_sender_check_timeouts(&sender, 25, retrans, MAX_WINDOW_SIZE);
    printf("Go-Back-N повторює %d кадрів починаючи з base=%u:\n", n, sender.s_base);
    for (int i = 0; i < n; i++) {
        printf("  [TX-RETRY] Повтор кадру Seq=%u\n", retrans[i].seq);
    }

    return 0;
}
