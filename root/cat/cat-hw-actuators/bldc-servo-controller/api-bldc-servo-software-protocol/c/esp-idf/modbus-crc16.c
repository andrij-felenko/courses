#include <stdint.h>
#include <stddef.h>

// Обчислення контрольної суми CRC16 Modbus
uint16_t modbus_crc16(const uint8_t *buffer, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= buffer[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

// Формування кадру Modbus RTU для запису одного 16-бітного регістру (Функція 0x06)
size_t pack_modbus_write_frame(uint8_t slave_addr, uint16_t reg_addr, uint16_t reg_value, uint8_t *out_frame) {
    out_frame[0] = slave_addr;
    out_frame[1] = 0x06; // Write Single Register
    out_frame[2] = (uint8_t)(reg_addr >> 8);
    out_frame[3] = (uint8_t)(reg_addr & 0xFF);
    out_frame[4] = (uint8_t)(reg_value >> 8);
    out_frame[5] = (uint8_t)(reg_value & 0xFF);
    
    uint16_t crc = modbus_crc16(out_frame, 6);
    out_frame[6] = (uint8_t)(crc & 0xFF);        // LSB спочатку
    out_frame[7] = (uint8_t)((crc >> 8) & 0xFF); // MSB потім
    
    return 8; // Загальний розмір кадру в байтах
}
