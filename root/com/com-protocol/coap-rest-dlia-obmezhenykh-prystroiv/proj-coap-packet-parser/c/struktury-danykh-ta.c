#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#define COAP_HEADER_SIZE 4
#define COAP_PAYLOAD_MARKER 0xFF
#define COAP_MAX_OPTIONS 16

typedef enum {
    COAP_TYPE_CON = 0,
    COAP_TYPE_NON = 1,
    COAP_TYPE_ACK = 2,
    COAP_TYPE_RST = 3
} coap_type_t;

typedef struct {
    uint16_t number;
    uint16_t length;
    const uint8_t *value;
} coap_option_t;

typedef struct {
    uint8_t version;
    coap_type_t type;
    uint8_t token_len;
    uint8_t code;
    uint16_t message_id;
    uint8_t token[8];
    coap_option_t options[COAP_MAX_OPTIONS];
    size_t option_count;
    const uint8_t *payload;
    size_t payload_len;
} coap_packet_t;

/* Розбір вхідної UDP-датаграми у структуру coap_packet_t */
bool coap_parse(const uint8_t *buf, size_t len, coap_packet_t *pkt) {
    if (!buf || !pkt || len < COAP_HEADER_SIZE) {
        return false;
    }

    memset(pkt, 0, sizeof(*pkt));

    pkt->version = (buf[0] >> 6) & 0x03;
    if (pkt->version != 1) {
        return false; /* Непідтримувана версія CoAP */
    }

    pkt->type = (coap_type_t)((buf[0] >> 4) & 0x03);
    pkt->token_len = buf[0] & 0x0F;
    if (pkt->token_len > 8) {
        return false; /* TKL більше 8 є неприпустимим */
    }

    pkt->code = buf[1];
    pkt->message_id = ((uint16_t)buf[2] << 8) | buf[3];

    size_t offset = COAP_HEADER_SIZE;
    if (len < offset + pkt->token_len) {
        return false;
    }

    if (pkt->token_len > 0) {
        memcpy(pkt->token, &buf[offset], pkt->token_len);
        offset += pkt->token_len;
    }

    uint16_t current_option_number = 0;

    while (offset < len) {
        if (buf[offset] == COAP_PAYLOAD_MARKER) {
            offset++; /* Пропускаємо маркер 0xFF */
            if (offset >= len) {
                return false; /* Маркер без тіла є помилкою синтаксису */
            }
            pkt->payload = &buf[offset];
            pkt->payload_len = len - offset;
            return true;
        }

        if (pkt->option_count >= COAP_MAX_OPTIONS) {
            return false; /* Переповнення статичної таблиці опцій */
        }

        uint8_t opt_header = buf[offset++];
        uint16_t delta = (opt_header >> 4) & 0x0F;
        uint16_t opt_len = opt_header & 0x0F;

        if (delta == 15 || opt_len == 15) {
            return false; /* Значення 15 зарезервовано для маркера */
        }

        /* Розширення Delta */
        if (delta == 13) {
            if (offset >= len) return false;
            delta = (uint16_t)buf[offset++] + 13;
        } else if (delta == 14) {
            if (offset + 1 >= len) return false;
            delta = (((uint16_t)buf[offset] << 8) | buf[offset + 1]) + 269;
            offset += 2;
        }

        /* Розширення Length */
        if (opt_len == 13) {
            if (offset >= len) return false;
            opt_len = (uint16_t)buf[offset++] + 13;
        } else if (opt_len == 14) {
            if (offset + 1 >= len) return false;
            opt_len = (((uint16_t)buf[offset] << 8) | buf[offset + 1]) + 269;
            offset += 2;
        }

        if (offset + opt_len > len) {
            return false;
        }

        current_option_number += delta;
        pkt->options[pkt->option_count].number = current_option_number;
        pkt->options[pkt->option_count].length = opt_len;
        pkt->options[pkt->option_count].value = &buf[offset];
        pkt->option_count++;

        offset += opt_len;
    }

    return true;
}

/* Серіалізація структури coap_packet_t у вихідний буфер */
size_t coap_serialize(const coap_packet_t *pkt, uint8_t *out, size_t max_len) {
    if (!pkt || !out || max_len < (size_t)(COAP_HEADER_SIZE + pkt->token_len)) {
        return 0;
    }

    out[0] = (uint8_t)((1 << 6) | ((pkt->type & 0x03) << 4) | (pkt->token_len & 0x0F));
    out[1] = pkt->code;
    out[2] = (uint8_t)(pkt->message_id >> 8);
    out[3] = (uint8_t)(pkt->message_id & 0xFF);

    size_t offset = COAP_HEADER_SIZE;
    if (pkt->token_len > 0) {
        memcpy(&out[offset], pkt->token, pkt->token_len);
        offset += pkt->token_len;
    }

    uint16_t prev_opt_num = 0;
    for (size_t i = 0; i < pkt->option_count; i++) {
        const coap_option_t *opt = &pkt->options[i];
        if (opt->number < prev_opt_num) {
            return 0; /* Порушено обов'язкове сортування опцій */
        }

        uint16_t delta = opt->number - prev_opt_num;
        uint8_t d_header = (delta < 13) ? (uint8_t)delta : (delta < 269 ? 13 : 14);
        uint8_t l_header = (opt->length < 13) ? (uint8_t)opt->length : (opt->length < 269 ? 13 : 14);

        if (offset >= max_len) return 0;
        out[offset++] = (uint8_t)((d_header << 4) | l_header);

        if (d_header == 13) {
            if (offset >= max_len) return 0;
            out[offset++] = (uint8_t)(delta - 13);
        } else if (d_header == 14) {
            if (offset + 1 >= max_len) return 0;
            uint16_t ext = delta - 269;
            out[offset++] = (uint8_t)(ext >> 8);
            out[offset++] = (uint8_t)(ext & 0xFF);
        }

        if (l_header == 13) {
            if (offset >= max_len) return 0;
            out[offset++] = (uint8_t)(opt->length - 13);
        } else if (l_header == 14) {
            if (offset + 1 >= max_len) return 0;
            uint16_t ext = opt->length - 269;
            out[offset++] = (uint8_t)(ext >> 8);
            out[offset++] = (uint8_t)(ext & 0xFF);
        }

        if (offset + opt->length > max_len) return 0;
        memcpy(&out[offset], opt->value, opt->length);
        offset += opt->length;

        prev_opt_num = opt->number;
    }

    if (pkt->payload && pkt->payload_len > 0) {
        if (offset + 1 + pkt->payload_len > max_len) return 0;
        out[offset++] = COAP_PAYLOAD_MARKER;
        memcpy(&out[offset], pkt->payload, pkt->payload_len);
        offset += pkt->payload_len;
    }

    return offset;
}
