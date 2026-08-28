#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Типи вузлів LwM2M TLV (біти 7-6) */
typedef enum {
    LWM2M_TLV_OBJECT_INSTANCE   = 0x00,
    LWM2M_TLV_RESOURCE_INSTANCE = 0x01,
    LWM2M_TLV_MULTIPLE_RESOURCE = 0x02,
    LWM2M_TLV_RESOURCE          = 0x03
} lwm2m_tlv_type_t;

/* Структура розпарсеного елемента TLV */
typedef struct {
    lwm2m_tlv_type_t type;
    uint16_t id;
    uint32_t length;
    const uint8_t *value;
} lwm2m_tlv_record_t;

/*
 * Декодування одного елемента TLV з буфера.
 * Повертає кількість спожитих байтів з буфера (0 у разі помилки або браку даних).
 */
size_t lwm2m_tlv_decode(const uint8_t *buf, size_t buf_len, lwm2m_tlv_record_t *out_rec) {
    if (buf == NULL || out_rec == NULL || buf_len < 2) {
        return 0;
    }

    size_t offset = 0;
    uint8_t type_byte = buf[offset++];

    /* 1. Витягуємо тип вузла */
    out_rec->type = (lwm2m_tlv_type_t)((type_byte >> 6) & 0x03);
    uint8_t id_len_flag = (type_byte >> 5) & 0x01;
    uint8_t len_type = (type_byte >> 3) & 0x03;
    uint8_t val_len_bits = type_byte & 0x07;

    /* 2. Декодуємо ідентифікатор ID */
    if (id_len_flag == 0) {
        /* 8-бітний ID */
        out_rec->id = buf[offset++];
    } else {
        /* 16-бітний ID (Big-Endian) */
        if (offset + 2 > buf_len) return 0;
        out_rec->id = ((uint16_t)buf[offset] << 8) | (uint16_t)buf[offset + 1];
        offset += 2;
    }

    /* 3. Декодуємо довжину Length */
    uint32_t length = 0;
    if (len_type == 0x00) {
        length = val_len_bits;
    } else if (len_type == 0x01) {
        if (offset + 1 > buf_len) return 0;
        length = buf[offset++];
    } else if (len_type == 0x02) {
        if (offset + 2 > buf_len) return 0;
        length = ((uint32_t)buf[offset] << 8) | (uint32_t)buf[offset + 1];
        offset += 2;
    } else if (len_type == 0x03) {
        if (offset + 3 > buf_len) return 0;
        length = ((uint32_t)buf[offset] << 16) | ((uint32_t)buf[offset + 1] << 8) | (uint32_t)buf[offset + 2];
        offset += 3;
    }

    /* 4. Перевірка наявності даних у буфері */
    if (offset + length > buf_len) {
        return 0; /* Неповний пакет */
    }

    out_rec->length = length;
    out_rec->value = (length > 0) ? &buf[offset] : NULL;
    offset += length;

    return offset;
}

/* Допоміжні функції читання значень */
bool lwm2m_tlv_get_int64(const lwm2m_tlv_record_t *rec, int64_t *val) {
    if (rec == NULL || val == NULL || rec->length == 0 || rec->length > 8) return false;
    int64_t res = 0;
    /* Знакове розширення для першого байта */
    if (rec->value[0] & 0x80) {
        res = -1;
    }
    for (size_t i = 0; i < rec->length; i++) {
        res = (res << 8) | rec->value[i];
    }
    *val = res;
    return true;
}

bool lwm2m_tlv_get_float(const lwm2m_tlv_record_t *rec, float *val) {
    if (rec == NULL || val == NULL || rec->length != 4) return false;
    union {
        uint32_t u;
        float f;
    } conv;
    conv.u = ((uint32_t)rec->value[0] << 24) |
             ((uint32_t)rec->value[1] << 16) |
             ((uint32_t)rec->value[2] << 8)  |
             (uint32_t)rec->value[3];
    *val = conv.f;
    return true;
}

/* Кодування одного числового ресурсу (int32) у TLV буфер */
size_t lwm2m_tlv_encode_int32(uint8_t *buf, size_t buf_len, uint16_t res_id, int32_t value) {
    /* Визначаємо мінімальну кількість байтів для збереження числа */
    uint8_t val_buf[4];
    size_t val_len = 0;

    if (value >= -128 && value <= 127) {
        val_buf[0] = (uint8_t)(value & 0xFF);
        val_len = 1;
    } else if (value >= -32768 && value <= 32767) {
        val_buf[0] = (uint8_t)((value >> 8) & 0xFF);
        val_buf[1] = (uint8_t)(value & 0xFF);
        val_len = 2;
    } else {
        val_buf[0] = (uint8_t)((value >> 24) & 0xFF);
        val_buf[1] = (uint8_t)((value >> 16) & 0xFF);
        val_buf[2] = (uint8_t)((value >> 8) & 0xFF);
        val_buf[3] = (uint8_t)(value & 0xFF);
        val_len = 4;
    }

    size_t header_len = 1 + (res_id > 255 ? 2 : 1);
    if (header_len + val_len > buf_len) return 0;

    size_t offset = 0;
    uint8_t type_byte = (LWM2M_TLV_RESOURCE << 6);
    if (res_id > 255) {
        type_byte |= (1 << 5); /* 16-бітний ID */
    }
    type_byte |= (uint8_t)(val_len & 0x07); /* Довжина 0..7 у бітах 2-0 */

    buf[offset++] = type_byte;
    if (res_id > 255) {
        buf[offset++] = (uint8_t)((res_id >> 8) & 0xFF);
        buf[offset++] = (uint8_t)(res_id & 0xFF);
    } else {
        buf[offset++] = (uint8_t)(res_id & 0xFF);
    }

    memcpy(&buf[offset], val_buf, val_len);
    offset += val_len;

    return offset;
}
