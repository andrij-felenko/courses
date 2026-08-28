#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди помилок парсера Modbus RTU */
typedef enum {
    MODBUS_OK = 0,
    MODBUS_ERR_FRAME_TOO_SHORT,
    MODBUS_ERR_ADDRESS_MISMATCH,
    MODBUS_ERR_CRC_INVALID,
    MODBUS_ERR_EXCEPTION_RESPONSE
} modbus_status_t;

/* Структура розібраного кадру */
typedef struct {
    uint8_t slave_addr;
    uint8_t function_code;
    bool is_exception;
    uint8_t exception_code;
    const uint8_t *payload;
    size_t payload_len;
} modbus_frame_t;

/* Обчислення Modbus CRC-16 за поліномом 0xA001 */
uint16_t modbus_crc16(const uint8_t *buffer, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= buffer[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

/* Парсер вхідного кадру Modbus RTU */
modbus_status_t modbus_rtu_parse(const uint8_t *buffer, size_t length,
                                  uint8_t my_address, modbus_frame_t *out_frame) {
    /* Мінімальний кадр RTU: Адреса (1) + Код (1) + CRC (2) = 4 байти */
    if (length < 4) {
        return MODBUS_ERR_FRAME_TOO_SHORT;
    }

    /* Перевірка контрольної суми CRC-16 */
    uint16_t calculated_crc = modbus_crc16(buffer, length - 2);
    uint16_t rx_crc = (uint16_t)buffer[length - 2] | ((uint16_t)buffer[length - 1] << 8);

    if (calculated_crc != rx_crc) {
        return MODBUS_ERR_CRC_INVALID;
    }

    uint8_t addr = buffer[0];
    /* Фільтрація адреси (якщо my_address == 0, приймаємо будь-яку) */
    if (my_address != 0 && addr != my_address && addr != 0) {
        return MODBUS_ERR_ADDRESS_MISMATCH;
    }

    out_frame->slave_addr = addr;
    uint8_t fc = buffer[1];

    /* Перевірка прапорця винятку (старший біт 0x80) */
    if (fc & 0x80) {
        out_frame->function_code = fc & 0x7F;
        out_frame->is_exception = true;
        out_frame->exception_code = (length > 4) ? buffer[2] : 0;
        out_frame->payload = NULL;
        out_frame->payload_len = 0;
        return MODBUS_ERR_EXCEPTION_RESPONSE;
    }

    out_frame->function_code = fc;
    out_frame->is_exception = false;
    out_frame->exception_code = 0;
    out_frame->payload = &buffer[2];
    out_frame->payload_len = length - 4; /* Віднімаємо адресу, код та 2 байти CRC */

    return MODBUS_OK;
}
