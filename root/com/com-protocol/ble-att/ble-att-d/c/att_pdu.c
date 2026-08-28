// att_pdu.h та att_pdu.c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define ATT_OP_ERROR_RSP   0x01
#define ATT_OP_WRITE_REQ   0x12
#define ATT_OP_WRITE_RSP   0x13

// Пакування кадру Write Request у буфер передачі L2CAP
// Повертає загальну довжину сформованого кадру ATT PDU
size_t att_build_write_req(uint8_t* out_buf, size_t max_len, 
                           uint16_t handle, const uint8_t* payload, size_t payload_len) {
    if (out_buf == NULL || payload == NULL) return 0;
    if (max_len < (3 + payload_len)) return 0; // Перевірка виходу за межі буфера

    out_buf[0] = ATT_OP_WRITE_REQ;             // 1 байт: Opcode (0x12)
    out_buf[1] = (uint8_t)(handle & 0xFF);      // 2 байти: Handle (Little-Endian)
    out_buf[2] = (uint8_t)((handle >> 8) & 0xFF);

    memcpy(&out_buf[3], payload, payload_len); // Корисні дані
    return 3 + payload_len;
}

// Обробка прийнятої відповіді сервера
typedef enum {
    ATT_STATUS_SUCCESS,
    ATT_STATUS_ERROR,
    ATT_STATUS_INVALID_PDU
} att_status_t;

att_status_t att_parse_response(const uint8_t* in_buf, size_t in_len, uint8_t* out_err_code) {
    if (in_buf == NULL || in_len < 1) return ATT_STATUS_INVALID_PDU;

    uint8_t opcode = in_buf[0];
    if (opcode == ATT_OP_WRITE_RSP) {
        return ATT_STATUS_SUCCESS; // Успішне підтвердження запису
    }

    if (opcode == ATT_OP_ERROR_RSP) {
        if (in_len < 5) return ATT_STATUS_INVALID_PDU; // Довжина Error Response рівно 5 байтів
        if (out_err_code) *out_err_code = in_buf[4];   // Байт ErrorCode за зміщенням 4
        return ATT_STATUS_ERROR;
    }

    return ATT_STATUS_INVALID_PDU;
}
