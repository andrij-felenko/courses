#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Специфікатори команд SDO у бітах 7..5 */
#define SDO_CCS_WRITE_REQ  1U
#define SDO_SCS_WRITE_RESP 3U
#define SDO_CCS_READ_REQ   2U
#define SDO_SCS_READ_RESP  2U
#define SDO_SCS_ABORT      4U

/* Канонічні коди помилок SDO Abort */
#define SDO_ABORT_TOGGLE_BIT         0x05030000UL
#define SDO_ABORT_TIMEOUT            0x05040001UL
#define SDO_ABORT_UNSUPPORTED_ACCESS 0x06010000UL
#define SDO_ABORT_READ_ONLY          0x06010002UL
#define SDO_ABORT_OBJECT_NOT_EXIST   0x06020000UL
#define SDO_ABORT_SUBINDEX_NOT_EXIST 0x06090011UL
#define SDO_ABORT_VALUE_OUT_OF_RANGE 0x06090030UL

typedef struct {
    uint8_t data[8];
} canopen_frame_payload_t;

typedef struct {
    uint16_t index;
    uint8_t subindex;
    uint32_t data;
    uint8_t data_len;
    bool is_abort;
    uint32_t abort_code;
} sdo_packet_t;

/* 
 * Формування кадру SDO Write Request (Initiate Download Expedited).
 * Формує 8-байтове корисне навантаження кадру CAN для запису значення до 4 байтів.
 */
bool canopen_sdo_pack_write_req(uint16_t index, uint8_t subindex, 
                                uint32_t data, uint8_t data_len, 
                                canopen_frame_payload_t *out_frame) {
    if (!out_frame || data_len < 1 || data_len > 4) {
        return false;
    }

    uint8_t empty_bytes = 4U - data_len;
    /* Bit 7..5: ccs=1 (Write), Bit 3..2: n (empty bytes), Bit 1: e=1 (Expedited), Bit 0: s=1 (Size) */
    uint8_t cmd = (SDO_CCS_WRITE_REQ << 5) | (empty_bytes << 2) | 0x02U | 0x01U;

    out_frame->data[0] = cmd;
    out_frame->data[1] = (uint8_t)(index & 0xFFU);
    out_frame->data[2] = (uint8_t)((index >> 8) & 0xFFU);
    out_frame->data[3] = subindex;

    /* Копіювання 32-бітного значення у порядку Little Endian */
    out_frame->data[4] = (uint8_t)(data & 0xFFU);
    out_frame->data[5] = (uint8_t)((data >> 8) & 0xFFU);
    out_frame->data[6] = (uint8_t)((data >> 16) & 0xFFU);
    out_frame->data[7] = (uint8_t)((data >> 24) & 0xFFU);

    return true;
}

/* 
 * Формування кадру SDO Read Request (Initiate Upload Request).
 * Формує запит на зчитування значення за вказаним індексом та субіндексом.
 */
bool canopen_sdo_pack_read_req(uint16_t index, uint8_t subindex, 
                               canopen_frame_payload_t *out_frame) {
    if (!out_frame) {
        return false;
    }

    /* Bit 7..5: ccs=2 (Read Request), решта бітів 0 */
    out_frame->data[0] = (SDO_CCS_READ_REQ << 5);
    out_frame->data[1] = (uint8_t)(index & 0xFFU);
    out_frame->data[2] = (uint8_t)((index >> 8) & 0xFFU);
    out_frame->data[3] = subindex;
    
    memset(&out_frame->data[4], 0, 4);
    return true;
}

/* 
 * Розбір відповіді SDO Read Response (Initiate Upload Response).
 * Розпаковує 8-байтовий кадр відповіді, витягує індекс, субіндекс, дані або код помилки Abort.
 */
bool canopen_sdo_parse_read_resp(const canopen_frame_payload_t *frame, 
                                 sdo_packet_t *out_packet) {
    if (!frame || !out_packet) {
        return false;
    }

    uint8_t cmd = frame->data[0];
    uint8_t scs = (cmd >> 5) & 0x07U;

    out_packet->index = (uint16_t)frame->data[1] | ((uint16_t)frame->data[2] << 8);
    out_packet->subindex = frame->data[3];

    /* Перевірка на кадр відмови SDO Abort (SCS = 4) */
    if (scs == SDO_SCS_ABORT) {
        out_packet->is_abort = true;
        out_packet->abort_code = (uint32_t)frame->data[4] |
                                 ((uint32_t)frame->data[5] << 8) |
                                 ((uint32_t)frame->data[6] << 16) |
                                 ((uint32_t)frame->data[7] << 24);
        out_packet->data = 0;
        out_packet->data_len = 0;
        return true;
    }

    if (scs != SDO_SCS_READ_RESP) {
        return false; /* Невідомий або невідповідний тип кадру SDO */
    }

    out_packet->is_abort = false;
    out_packet->abort_code = 0;

    uint8_t empty_bytes = (cmd >> 2) & 0x03U;
    out_packet->data_len = 4U - empty_bytes;

    out_packet->data = (uint32_t)frame->data[4] |
                       ((uint32_t)frame->data[5] << 8) |
                       ((uint32_t)frame->data[6] << 16) |
                       ((uint32_t)frame->data[7] << 24);

    return true;
}
