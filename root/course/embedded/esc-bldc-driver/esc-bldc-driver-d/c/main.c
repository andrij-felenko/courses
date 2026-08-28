#include <stdint.h>

// CRC DShot: згортаємо 12 бітів у 4, XOR-ом по тетрадах (по 4 біти)
uint8_t dshot_crc(uint16_t value) {     // value = (газ << 1) | біт_телеметрії, 12 бітів
    uint16_t c = value ^ (value >> 4) ^ (value >> 8);
    return c & 0x0F;                    // лишаємо молодші 4 біти
}

// зібрати повний 16-бітний кадр із газу (0..2047) і прапорця телеметрії
uint16_t dshot_frame(uint16_t throttle, uint8_t telemetry) {
    uint16_t value = (throttle << 1) | (telemetry & 1);   // 11 + 1 = 12 бітів
    return (value << 4) | dshot_crc(value);               // + 4 біти CRC = 16
}
