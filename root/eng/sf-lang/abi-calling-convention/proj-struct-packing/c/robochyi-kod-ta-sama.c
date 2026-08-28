#include <stdint.h>
#include <stddef.h>   // offsetof

// ── Звичайна структура: компілятор вставляє набивку ──
struct SensorPacket {
    uint8_t  msg_id;
    uint32_t timestamp;
    int16_t  temperature;
    uint8_t  flags;
};

// ── Та сама структура, запакована: набивки нема ──
struct __attribute__((packed)) SensorPacketPacked {
    uint8_t  msg_id;
    uint32_t timestamp;
    int16_t  temperature;
    uint8_t  flags;
};
