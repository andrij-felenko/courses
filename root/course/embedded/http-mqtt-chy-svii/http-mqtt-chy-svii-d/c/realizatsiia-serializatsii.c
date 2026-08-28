// Формування та перевірка цілісності бінарного кадру (C99)
#include <stdint.h>
#include <string.h>

#define FRAME_MAGIC 0xA5
#define MSG_TELEMETRY 0x01

static uint16_t calc_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000) crc = (crc << 1) ^ 0x1021;
            else crc = crc << 1;
        }
    }
    return crc;
}

size_t pack_telemetry_frame(uint16_t seq, uint32_t ts, int16_t temp, 
                            uint16_t hum, uint16_t vbat, uint8_t *buf, size_t max_len) 
{
    if (max_len < sizeof(sensor_packet_t)) return 0;
    
    sensor_packet_t pkt;
    pkt.magic = FRAME_MAGIC;
    pkt.msg_type = MSG_TELEMETRY;
    pkt.seq_num = seq;
    pkt.timestamp = ts;
    pkt.temperature = temp;
    pkt.humidity = hum;
    pkt.vbat_mv = vbat;
    
    // Рахуємо CRC по всій структурі за винятком самого поля crc16
    pkt.crc16 = calc_crc16((const uint8_t *)&pkt, sizeof(sensor_packet_t) - 2);
    
    memcpy(buf, &pkt, sizeof(sensor_packet_t));
    return sizeof(sensor_packet_t);
}
