static uint32_t get_u32_le(const uint8_t *buf) {
    return  (uint32_t)buf[0]
         | ((uint32_t)buf[1] <<  8)
         | ((uint32_t)buf[2] << 16)
         | ((uint32_t)buf[3] << 24);
}

static uint16_t get_u16_le(const uint8_t *buf) {
    return (uint16_t)(buf[0] | (buf[1] << 8));
}

// Десеріалізація: 8 байтів дроту → структура. Заповнюємо ЗВИЧАЙНУ структуру.
void unpack_sensor(const uint8_t *in, struct SensorPacket *p) {
    p->msg_id      = in[0];
    p->timestamp   = get_u32_le(&in[1]);
    p->temperature = (int16_t)get_u16_le(&in[5]);
    p->flags       = in[7];
}
