#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define PROTOCOL_MAX_PAYLOAD  128
#define PROTOCOL_MAX_PACKET   (sizeof(FrameHeader_t) + PROTOCOL_MAX_PAYLOAD + sizeof(uint16_t))
#define PROTOCOL_MAX_ENCODED  (PROTOCOL_MAX_PACKET + (PROTOCOL_MAX_PACKET / 254) + 2)

#pragma pack(push, 1)
typedef struct {
    uint8_t  msg_id;       // Ідентифікатор типу повідомлення
    uint8_t  seq_num;      // Порядковий номер кадру (0..255)
    uint16_t payload_len;  // Довжина корисного навантаження (Little-Endian)
} FrameHeader_t;
#pragma pack(pop)

// Швидкий розрахунок CRC-16-CCITT (поліном 0x1021, початкове значення 0xFFFF)
static inline uint16_t crc16_update(uint16_t crc, uint8_t data) {
    data ^= (uint8_t)(crc >> 8);
    data ^= (uint8_t)(data >> 4);
    return (uint16_t)((crc << 8) ^ ((uint16_t)data << 12) ^ 
                      ((uint16_t)data << 5) ^ (uint16_t)data);
}

uint16_t crc16_calculate(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc = crc16_update(crc, data[i]);
    }
    return crc;
}
