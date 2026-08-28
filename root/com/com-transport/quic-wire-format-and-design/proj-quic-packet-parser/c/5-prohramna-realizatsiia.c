#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define QUIC_MAX_CID_LEN 20
#define QUIC_VERSION_1   0x00000001

typedef enum {
    QUIC_OK = 0,
    QUIC_ERR_BUFFER_TOO_SHORT,
    QUIC_ERR_INVALID_VARINT,
    QUIC_ERR_INVALID_VERSION,
    QUIC_ERR_CID_TOO_LONG,
    QUIC_ERR_UNKNOWN_FRAME
} quic_status_t;

typedef enum {
    QUIC_PKT_INITIAL   = 0x00,
    QUIC_PKT_0RTT      = 0x01,
    QUIC_PKT_HANDSHAKE = 0x02,
    QUIC_PKT_RETRY     = 0x03,
    QUIC_PKT_1RTT_SHORT
} quic_pkt_type_t;

typedef struct {
    uint8_t len;
    uint8_t data[QUIC_MAX_CID_LEN];
} quic_cid_t;

typedef struct {
    quic_pkt_type_t type;
    bool is_long_header;
    uint32_t version;
    quic_cid_t dcid;
    quic_cid_t scid;
    const uint8_t *token;
    size_t token_len;
    uint64_t payload_len;
    const uint8_t *payload;
} quic_header_t;

typedef struct {
    uint64_t stream_id;
    uint64_t offset;
    uint64_t length;
    bool fin;
    const uint8_t *data;
} quic_stream_frame_t;

typedef struct {
    uint64_t largest_acked;
    uint64_t ack_delay;
    uint64_t first_ack_range;
    uint64_t range_count;
} quic_ack_frame_t;

/* Декодування цілого числа змінної довжини (RFC 9000 §16) */
quic_status_t quic_read_varint(const uint8_t **buf, size_t *buf_len, uint64_t *val) {
    if (*buf_len == 0) return QUIC_ERR_BUFFER_TOO_SHORT;

    uint8_t first = **buf;
    uint8_t prefix = (first >> 6) & 0x03;
    size_t len = (size_t)1 << prefix;

    if (*buf_len < len) return QUIC_ERR_BUFFER_TOO_SHORT;

    uint64_t res = first & 0x3F;
    (*buf)++;
    (*buf_len)--;

    for (size_t i = 1; i < len; i++) {
        res = (res << 8) | (**buf);
        (*buf)++;
        (*buf_len)--;
    }

    *val = res;
    return QUIC_OK;
}

/* Розбір незахищеного заголовка пакета QUIC */
quic_status_t quic_parse_header(const uint8_t *raw, size_t raw_len,
                                size_t dcid_len_for_short, quic_header_t *hdr) {
    if (raw_len < 1) return QUIC_ERR_BUFFER_TOO_SHORT;

    const uint8_t *p = raw;
    size_t rem = raw_len;
    uint8_t first_byte = *p++;
    rem--;

    hdr->is_long_header = (first_byte & 0x80) != 0;

    if (hdr->is_long_header) {
        if (rem < 4) return QUIC_ERR_BUFFER_TOO_SHORT;
        hdr->version = ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
                       ((uint32_t)p[2] << 8)  | ((uint32_t)p[3]);
        p += 4; rem -= 4;

        uint8_t type_bits = (first_byte >> 4) & 0x03;
        hdr->type = (quic_pkt_type_t)type_bits;

        /* DCID */
        if (rem < 1) return QUIC_ERR_BUFFER_TOO_SHORT;
        hdr->dcid.len = *p++; rem--;
        if (hdr->dcid.len > QUIC_MAX_CID_LEN) return QUIC_ERR_CID_TOO_LONG;
        if (rem < hdr->dcid.len) return QUIC_ERR_BUFFER_TOO_SHORT;
        memcpy(hdr->dcid.data, p, hdr->dcid.len);
        p += hdr->dcid.len; rem -= hdr->dcid.len;

        /* SCID */
        if (rem < 1) return QUIC_ERR_BUFFER_TOO_SHORT;
        hdr->scid.len = *p++; rem--;
        if (hdr->scid.len > QUIC_MAX_CID_LEN) return QUIC_ERR_CID_TOO_LONG;
        if (rem < hdr->scid.len) return QUIC_ERR_BUFFER_TOO_SHORT;
        memcpy(hdr->scid.data, p, hdr->scid.len);
        p += hdr->scid.len; rem -= hdr->scid.len;

        /* Initial Token */
        if (hdr->type == QUIC_PKT_INITIAL) {
            uint64_t tlen = 0;
            quic_status_t st = quic_read_varint(&p, &rem, &tlen);
            if (st != QUIC_OK) return st;
            if (rem < tlen) return QUIC_ERR_BUFFER_TOO_SHORT;
            hdr->token = p;
            hdr->token_len = (size_t)tlen;
            p += tlen; rem -= tlen;
        } else {
            hdr->token = NULL;
            hdr->token_len = 0;
        }

        /* Payload Length */
        uint64_t plen = 0;
        quic_status_t st = quic_read_varint(&p, &rem, &plen);
        if (st != QUIC_OK) return st;
        if (rem < plen) return QUIC_ERR_BUFFER_TOO_SHORT;

        hdr->payload_len = plen;
        hdr->payload = p;
    } else {
        /* Short Header (1-RTT) */
        hdr->type = QUIC_PKT_1RTT_SHORT;
        hdr->version = 0;
        hdr->scid.len = 0;
        hdr->token = NULL;
        hdr->token_len = 0;

        if (dcid_len_for_short > QUIC_MAX_CID_LEN) return QUIC_ERR_CID_TOO_LONG;
        if (rem < dcid_len_for_short) return QUIC_ERR_BUFFER_TOO_SHORT;

        hdr->dcid.len = (uint8_t)dcid_len_for_short;
        memcpy(hdr->dcid.data, p, dcid_len_for_short);
        p += dcid_len_for_short; rem -= dcid_len_for_short;

        hdr->payload_len = rem;
        hdr->payload = p;
    }

    return QUIC_OK;
}

/* Розбір кадру STREAM з розшифрованого корисного навантаження */
quic_status_t quic_parse_stream_frame(const uint8_t *payload, size_t payload_len,
                                      quic_stream_frame_t *frame) {
    if (payload_len < 1) return QUIC_ERR_BUFFER_TOO_SHORT;

    const uint8_t *p = payload;
    size_t rem = payload_len;
    uint8_t ftype = *p++;
    rem--;

    if (ftype < 0x08 || ftype > 0x0F) return QUIC_ERR_UNKNOWN_FRAME;

    bool has_off = (ftype & 0x04) != 0;
    bool has_len = (ftype & 0x02) != 0;
    frame->fin   = (ftype & 0x01) != 0;

    /* Stream ID */
    quic_status_t st = quic_read_varint(&p, &rem, &frame->stream_id);
    if (st != QUIC_OK) return st;

    /* Offset */
    if (has_off) {
        st = quic_read_varint(&p, &rem, &frame->offset);
        if (st != QUIC_OK) return st;
    } else {
        frame->offset = 0;
    }

    /* Length & Data */
    if (has_len) {
        st = quic_read_varint(&p, &rem, &frame->length);
        if (st != QUIC_OK) return st;
        if (rem < frame->length) return QUIC_ERR_BUFFER_TOO_SHORT;
        frame->data = p;
    } else {
        frame->length = rem;
        frame->data = p;
    }

    return QUIC_OK;
}

/* Розбір кадру ACK */
quic_status_t quic_parse_ack_frame(const uint8_t *payload, size_t payload_len,
                                   quic_ack_frame_t *ack) {
    if (payload_len < 1) return QUIC_ERR_BUFFER_TOO_SHORT;

    const uint8_t *p = payload;
    size_t rem = payload_len;
    uint8_t ftype = *p++;
    rem--;

    if (ftype != 0x02 && ftype != 0x03) return QUIC_ERR_UNKNOWN_FRAME;

    quic_status_t st = quic_read_varint(&p, &rem, &ack->largest_acked);
    if (st != QUIC_OK) return st;

    st = quic_read_varint(&p, &rem, &ack->ack_delay);
    if (st != QUIC_OK) return st;

    st = quic_read_varint(&p, &rem, &ack->range_count);
    if (st != QUIC_OK) return st;

    st = quic_read_varint(&p, &rem, &ack->first_ack_range);
    if (st != QUIC_OK) return st;

    return QUIC_OK;
}
