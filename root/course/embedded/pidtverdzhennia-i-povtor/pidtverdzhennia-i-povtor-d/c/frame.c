/* frame.c — CRC16-CCITT та пакування/розбір кадру ARQ.
 *
 * Свідомо не шлемо структуру в лінію байтами `memcpy` зі структури:
 * вирівнювання й порядок байтів на двох різних МК не збігаються, а «діри»
 * від вирівнювання ще й потрапили б під CRC із випадковим умістом.
 */
#include "arq.h"

#include <string.h>

uint16_t arq_crc16(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFFu; /* CRC-16/CCITT-FALSE, поліном 0x1021 */
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (unsigned bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

size_t arq_encode(const arq_frame *f, uint8_t *out, size_t out_cap)
{
    if (f->len > ARQ_MAX_PAYLOAD) {
        return 0;
    }
    const size_t total = ARQ_HDR_LEN + (size_t)f->len + ARQ_CRC_LEN;
    if (out_cap < total) {
        return 0;
    }

    out[0] = ARQ_SOF;
    out[1] = f->type;
    out[2] = (uint8_t)(f->seq & 1u);
    out[3] = f->len;
    if (f->len > 0) {
        memcpy(out + ARQ_HDR_LEN, f->payload, f->len);
    }

    /* CRC накриває все, крім самого SOF: маркер синхронізації не є даними. */
    const uint16_t crc = arq_crc16(out + 1, 3u + (size_t)f->len);
    out[total - 2] = (uint8_t)(crc & 0xFFu);
    out[total - 1] = (uint8_t)(crc >> 8);
    return total;
}

arq_decode_res arq_decode(const uint8_t *wire, size_t len, arq_frame *out)
{
    if (len < ARQ_HDR_LEN + ARQ_CRC_LEN) {
        return ARQ_DEC_TOO_SHORT;
    }
    if (wire[0] != ARQ_SOF) {
        return ARQ_DEC_NO_SOF;
    }

    const size_t payload_len = wire[3];
    if (payload_len > ARQ_MAX_PAYLOAD) {
        return ARQ_DEC_BAD_LEN;
    }
    if (len != ARQ_HDR_LEN + payload_len + ARQ_CRC_LEN) {
        return ARQ_DEC_BAD_LEN;
    }

    /* Спершу CRC: далі можна вірити полям заголовка. */
    const uint16_t got = (uint16_t)wire[len - 2] | (uint16_t)((uint16_t)wire[len - 1] << 8);
    if (arq_crc16(wire + 1, 3u + payload_len) != got) {
        return ARQ_DEC_BAD_CRC;
    }

    switch (wire[1]) {
    case ARQ_DATA:
        break;
    case ARQ_ACK:
    case ARQ_NACK:
        if (payload_len != 0) {
            return ARQ_DEC_BAD_LEN; /* квитанція з даними — не наш протокол */
        }
        break;
    default:
        return ARQ_DEC_BAD_TYPE;
    }

    if (wire[2] > 1u) {
        return ARQ_DEC_BAD_SEQ; /* у Stop-and-Wait номер однобітний */
    }

    out->type = wire[1];
    out->seq  = wire[2];
    out->len  = (uint8_t)payload_len;
    if (payload_len > 0) {
        memcpy(out->payload, wire + ARQ_HDR_LEN, payload_len);
    }
    return ARQ_DEC_OK;
}

const char *arq_decode_str(arq_decode_res res)
{
    switch (res) {
    case ARQ_DEC_OK:        return "ok";
    case ARQ_DEC_TOO_SHORT: return "закороткий кадр";
    case ARQ_DEC_NO_SOF:    return "немає SOF";
    case ARQ_DEC_BAD_LEN:   return "невірна довжина";
    case ARQ_DEC_BAD_TYPE:  return "невідомий тип";
    case ARQ_DEC_BAD_SEQ:   return "номер поза 0/1";
    case ARQ_DEC_BAD_CRC:   return "CRC не збігся";
    }
    return "?";
}
