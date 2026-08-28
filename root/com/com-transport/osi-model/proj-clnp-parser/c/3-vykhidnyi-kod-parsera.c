#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CLNP_NLPID_CLNP        0x81
#define CLNP_TYPE_DATA         0x1C
#define CLNP_TYPE_ERROR        0x01
#define CLNP_FLAG_SP           0x80
#define CLNP_FLAG_MS           0x40
#define CLNP_FLAG_ER           0x20

#define TP4_TYPE_DT            0xF0
#define TP4_TYPE_AK            0x70
#define TP4_TYPE_CR            0xE0
#define TP4_TYPE_CC            0xD0
#define TP4_TYPE_DR            0x80

/* Структура розібраного заголовка CLNP */
typedef struct {
    uint8_t nlpid;
    uint8_t header_len;
    uint8_t version;
    uint8_t lifetime;
    uint8_t flags;
    uint16_t segment_len;
    uint16_t checksum;
    bool is_segmented;
    bool more_segments;
    bool error_report;
    uint8_t type;

    uint8_t dst_nsap_len;
    const uint8_t *dst_nsap;
    uint8_t src_nsap_len;
    const uint8_t *src_nsap;

    uint16_t duid;
    uint16_t segment_offset;
    uint16_t total_len;

    const uint8_t *payload;
    size_t payload_len;
} clnp_packet_t;

/* Структура розібраного транспортного блоку даних TP4 */
typedef struct {
    uint8_t header_len;
    uint8_t type;
    uint16_t dst_ref;
    uint8_t tpdu_nr;
    bool eot;
    const uint8_t *data;
    size_t data_len;
} tp4_dt_packet_t;

/* Перевірка контрольної суми Флетчера-16 за стандартом ISO 8473 */
bool clnp_verify_fletcher16(const uint8_t *header, size_t len) {
    if (len == 0) return false;
    
    /* Якщо байти контрольної суми нульові (зміщення 7,8) — перевірку вимкнено */
    if (len >= 9 && header[7] == 0x00 && header[8] == 0x00) {
        return true;
    }

    uint32_t c0 = 0;
    uint32_t c1 = 0;

    for (size_t i = 0; i < len; ++i) {
        c0 += header[i];
        c1 += c0;
    }

    return ((c0 % 255) == 0) && ((c1 % 255) == 0);
}

/* Безпечний нуль-копіювальний розбір заголовка CLNP */
bool clnp_parse(const uint8_t *buf, size_t buf_len, clnp_packet_t *pkt) {
    if (!buf || buf_len < 9 || !pkt) return false;
    memset(pkt, 0, sizeof(*pkt));

    pkt->nlpid = buf[0];
    if (pkt->nlpid != CLNP_NLPID_CLNP) {
        return false; /* Невідомий мережевий протокол */
    }

    pkt->header_len = buf[1];
    if (pkt->header_len < 9 || pkt->header_len > buf_len) {
        return false; /* Некоректна довжина заголовка відносно буфера */
    }

    pkt->version = buf[2];
    pkt->lifetime = buf[3];
    pkt->flags = buf[4];
    pkt->type = pkt->flags & 0x1F;
    pkt->is_segmented = (pkt->flags & CLNP_FLAG_SP) != 0;
    pkt->more_segments = (pkt->flags & CLNP_FLAG_MS) != 0;
    pkt->error_report = (pkt->flags & CLNP_FLAG_ER) != 0;

    pkt->segment_len = ((uint16_t)buf[5] << 8) | buf[6];
    pkt->checksum = ((uint16_t)buf[7] << 8) | buf[8];

    /* Перевірка контрольної суми Флетчера */
    if (!clnp_verify_fletcher16(buf, pkt->header_len)) {
        return false; /* Помилка контрольної суми */
    }

    size_t offset = 9;

    /* Розбір адреси призначення NSAP */
    if (offset >= pkt->header_len) return false;
    pkt->dst_nsap_len = buf[offset++];
    if (pkt->dst_nsap_len > 20 || offset + pkt->dst_nsap_len > pkt->header_len) {
        return false; /* Порушення довжини NSAP */
    }
    pkt->dst_nsap = &buf[offset];
    offset += pkt->dst_nsap_len;

    /* Розбір адреси джерела NSAP */
    if (offset >= pkt->header_len) return false;
    pkt->src_nsap_len = buf[offset++];
    if (pkt->src_nsap_len > 20 || offset + pkt->src_nsap_len > pkt->header_len) {
        return false; /* Порушення довжини NSAP */
    }
    pkt->src_nsap = &buf[offset];
    offset += pkt->src_nsap_len;

    /* Розбір частини сегментації (якщо встановлено прапорець SP) */
    if (pkt->is_segmented) {
        if (offset + 6 > pkt->header_len) return false;
        pkt->duid = ((uint16_t)buf[offset] << 8) | buf[offset + 1];
        pkt->segment_offset = ((uint16_t)buf[offset + 2] << 8) | buf[offset + 3];
        pkt->total_len = ((uint16_t)buf[offset + 4] << 8) | buf[offset + 5];
        offset += 6;
    }

    /* Визначаємо межі корисного навантаження */
    pkt->payload = &buf[pkt->header_len];
    if (pkt->segment_len >= pkt->header_len && pkt->segment_len <= buf_len) {
        pkt->payload_len = pkt->segment_len - pkt->header_len;
    } else {
        pkt->payload_len = buf_len - pkt->header_len;
    }

    return true;
}

/* Розбір транспортного блоку даних TP4 DT-TPDU */
bool tp4_parse_dt(const uint8_t *buf, size_t buf_len, tp4_dt_packet_t *tp) {
    if (!buf || buf_len < 5 || !tp) return false;
    memset(tp, 0, sizeof(*tp));

    tp->header_len = buf[0];
    if (tp->header_len < 4 || (size_t)(tp->header_len + 1) > buf_len) {
        return false;
    }

    uint8_t type_byte = buf[1];
    if ((type_byte & 0xF0) != TP4_TYPE_DT) {
        return false; /* Очікувався DT-TPDU */
    }
    tp->type = type_byte & 0xF0;

    tp->dst_ref = ((uint16_t)buf[2] << 8) | buf[3];
    tp->eot = (buf[4] & 0x80) != 0;
    tp->tpdu_nr = buf[4] & 0x7F;

    tp->data = &buf[tp->header_len + 1];
    tp->data_len = buf_len - (tp->header_len + 1);

    return true;
}

/* Друк адреси NSAP у шістнадцятковому форматі */
void print_nsap(const uint8_t *nsap, uint8_t len) {
    for (uint8_t i = 0; i < len; ++i) {
        printf("%02X", nsap[i]);
        if (i % 2 == 1 && i != len - 1) {
            printf(".");
        }
    }
}
