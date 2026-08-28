#include <stdint.h>

// Структура без порожніх байтів вирівнювання
typedef struct __attribute__((packed)) {
    uint8_t  node_id;      // 1 байт
    uint32_t timestamp_ms; // 4 байти
    uint16_t packet_seq;   // 2 байти
    uint16_t crc16;        // 2 байти
} TelemetryPacketHeader;

_Static_assert(sizeof(TelemetryPacketHeader) == 9, "Розмір заголовка має бути рівно 9 байтів!");
