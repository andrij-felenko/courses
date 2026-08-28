#include <stdint.h>
#include <stddef.h>

// helper: покласти uint32 у буфер молодшим байтом уперед (little-endian)
static void put_u32_le(uint8_t *buf, uint32_t v) {
    buf[0] = (uint8_t)(v      );
    buf[1] = (uint8_t)(v >>  8);
    buf[2] = (uint8_t)(v >> 16);
    buf[3] = (uint8_t)(v >> 24);
}

static void put_u16_le(uint8_t *buf, uint16_t v) {
    buf[0] = (uint8_t)(v     );
    buf[1] = (uint8_t)(v >> 8);
}

// Серіалізація: структура → рівно 8 байтів дроту. Порядок і розрядність — наші.
// Повертає кількість записаних байтів.
size_t pack_sensor(const struct SensorPacket *p, uint8_t *out) {
    out[0] = p->msg_id;                                  // 1 байт
    put_u32_le(&out[1], p->timestamp);                   // 4 байти
    put_u16_le(&out[5], (uint16_t)p->temperature);       // 2 байти
    out[7] = p->flags;                                   // 1 байт
    return 8;
}
