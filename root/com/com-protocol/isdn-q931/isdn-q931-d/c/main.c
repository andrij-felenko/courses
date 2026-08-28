#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define Q931_PROTO_DISC_CALL_CONTROL 0x08

typedef struct {
    uint8_t  ie_id;
    uint8_t  length;
    const uint8_t *data;
} q931_ie_t;

typedef struct {
    uint8_t  protocol_discriminator;
    uint16_t call_reference_value;
    bool     call_ref_flag_destination;
    uint8_t  message_type;
    size_t   payload_offset;
} q931_header_t;

/* Безпечний розбір заголовка Q.931 з перевіркою меж буфера */
bool q931_parse_header(const uint8_t *buf, size_t len, q931_header_t *hdr) {
    if (!buf || len < 3 || !hdr) {
        return false;
    }

    hdr->protocol_discriminator = buf[0];
    if (hdr->protocol_discriminator != Q931_PROTO_DISC_CALL_CONTROL) {
        return false;
    }

    uint8_t cr_len = buf[1] & 0x0F;
    if (cr_len == 0) {
        /* Фіктивне посилання виклику (Dummy CRV) */
        hdr->call_reference_value = 0;
        hdr->call_ref_flag_destination = false;
        if (len < 3) return false;
        hdr->message_type = buf[2];
        hdr->payload_offset = 3;
        return true;
    } else if (cr_len == 1) {
        if (len < 4) return false;
        hdr->call_ref_flag_destination = (buf[2] & 0x80) != 0;
        hdr->call_reference_value = buf[2] & 0x7F;
        hdr->message_type = buf[3];
        hdr->payload_offset = 4;
        return true;
    } else if (cr_len == 2) {
        if (len < 5) return false;
        hdr->call_ref_flag_destination = (buf[2] & 0x80) != 0;
        hdr->call_reference_value = ((uint16_t)(buf[2] & 0x7F) << 8) | buf[3];
        hdr->message_type = buf[4];
        hdr->payload_offset = 5;
        return true;
    }

    return false; /* Непідтримувана довжина CRV */
}

/* Ітератор інформаційних елементів (IE) TLV */
bool q931_next_ie(const uint8_t *buf, size_t len, size_t *offset, q931_ie_t *ie) {
    if (!buf || !offset || !ie || *offset >= len) {
        return false;
    }

    uint8_t first = buf[*offset];
    if (first & 0x80) {
        /* Однобайтовий IE (Single-octet IE) */
        ie->ie_id = first & 0xF0;
        ie->length = 1;
        ie->data = &buf[*offset];
        *offset += 1;
        return true;
    }

    /* Багатобайтовий IE змінної довжини (TLV) */
    if (*offset + 2 > len) {
        return false; /* Пошкоджений пакет */
    }

    ie->ie_id = first;
    ie->length = buf[*offset + 1];
    *offset += 2;

    if (*offset + ie->length > len) {
        return false; /* Довжина виходить за межі буфера */
    }

    ie->data = &buf[*offset];
    *offset += ie->length;
    return true;
}
