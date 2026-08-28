#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PAYLOAD_SIZE 64
#define TOTAL_RX_SLOTS   4

typedef enum {
    FRAME_TYPE_DATA = 0x01,
    FRAME_TYPE_CREDIT_GRANT = 0x02
} FrameType;

typedef struct {
    uint8_t type;
    uint8_t seq_or_credit; // seq для DATA, кількість кредитів для GRANT
    uint8_t length;
    uint8_t payload[MAX_PAYLOAD_SIZE];
} PacketFrame;

// Передавач
typedef struct {
    int32_t available_credits;
    uint8_t next_seq;
} CreditSender;

void credit_sender_init(CreditSender *s, int32_t initial_credits) {
    s->available_credits = initial_credits;
    s->next_seq = 0;
}

bool credit_sender_can_send(const CreditSender *s) {
    return s->available_credits > 0;
}

bool credit_sender_send(CreditSender *s, const uint8_t *data, uint8_t len, PacketFrame *out_frame) {
    if (s->available_credits <= 0 || len > MAX_PAYLOAD_SIZE) {
        return false;
    }

    out_frame->type = FRAME_TYPE_DATA;
    out_frame->seq_or_credit = s->next_seq++;
    out_frame->length = len;
    memcpy(out_frame->payload, data, len);

    s->available_credits--;
    return true;
}

void credit_sender_on_grant(CreditSender *s, uint8_t returned_credits) {
    s->available_credits += returned_credits;
}

// Приймач
typedef struct {
    uint8_t pending_returns;
    uint8_t occupied_slots;
} CreditReceiver;

void credit_receiver_init(CreditReceiver *r) {
    r->pending_returns = 0;
    r->occupied_slots = 0;
}

bool credit_receiver_on_frame(CreditReceiver *r, const PacketFrame *frame) {
    if (frame->type != FRAME_TYPE_DATA) {
        return false;
    }
    if (r->occupied_slots >= TOTAL_RX_SLOTS) {
        return false; // Порушення протоколу: відправник перевищив квоту
    }
    r->occupied_slots++;
    return true;
}

// Викликається після того, як завдання вичитало пакет із пам'яті
void credit_receiver_release_slot(CreditReceiver *r) {
    if (r->occupied_slots > 0) {
        r->occupied_slots--;
        r->pending_returns++;
    }
}

bool credit_receiver_make_grant(CreditReceiver *r, PacketFrame *out_frame) {
    if (r->pending_returns == 0) {
        return false;
    }

    out_frame->type = FRAME_TYPE_CREDIT_GRANT;
    out_frame->seq_or_credit = r->pending_returns;
    out_frame->length = 0;

    r->pending_returns = 0;
    return true;
}
