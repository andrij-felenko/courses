#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Бінарна структура корисного навантаження HEARTBEAT
typedef struct __attribute__((__packed__)) {
    uint32_t custom_mode;
    uint8_t  type;
    uint8_t  autopilot;
    uint8_t  base_mode;
    uint8_t  system_status;
    uint8_t  mavlink_version;
} mavlink_heartbeat_payload_t;

// Функція ручної серіалізації в буфер (Little-Endian)
void pack_heartbeat(uint8_t* buffer, uint32_t custom_mode, uint8_t type,
                    uint8_t autopilot, uint8_t base_mode,
                    uint8_t system_status, uint8_t mavlink_version) {
    // 1. Серіалізація custom_mode (uint32_t) у Little-Endian
    buffer[0] = (uint8_t)(custom_mode & 0xFF);
    buffer[1] = (uint8_t)((custom_mode >> 8) & 0xFF);
    buffer[2] = (uint8_t)((custom_mode >> 16) & 0xFF);
    buffer[3] = (uint8_t)((custom_mode >> 24) & 0xFF);

    // 2. Серіалізація однобайтних полів
    buffer[4] = type;
    buffer[5] = autopilot;
    buffer[6] = base_mode;
    buffer[7] = system_status;
    buffer[8] = mavlink_version;
}

// Функція ручної десеріалізації з буфера
void unpack_heartbeat(const uint8_t* buffer, mavlink_heartbeat_payload_t* out) {
    out->custom_mode = (uint32_t)buffer[0] |
                       ((uint32_t)buffer[1] << 8) |
                       ((uint32_t)buffer[2] << 16) |
                       ((uint32_t)buffer[3] << 24);

    out->type            = buffer[4];
    out->autopilot       = buffer[5];
    out->base_mode       = buffer[6];
    out->system_status   = buffer[7];
    out->mavlink_version = buffer[8];
}
