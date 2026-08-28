#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TELEM_MAGIC        0x7E
#define TELEM_VERSION      0x01

#define MODE_ABSOLUTE      0x00
#define MODE_FORWARD_DELTA 0x01
#define MODE_REVERSE_DELTA 0x02

#define RTC_FLAG_UNSYNC    0x00
#define RTC_FLAG_ESTIMATED 0x04
#define RTC_FLAG_SYNCED    0x08

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;
    uint8_t  version;
    uint16_t flags;
    uint8_t  sample_count;
    uint8_t  sample_type;
    uint32_t anchor_sec;
} PacketHeader;
#pragma pack(pop)

typedef struct {
    uint32_t local_time_ms;
    int16_t  sensor_raw;
} SensorReading;

typedef struct {
    uint64_t timestamp_utc_ms;
    int16_t  sensor_raw;
} DecodedPoint;

// Пакування пачки замірів у бінарний кадр за методом зворотних дельт
int telemetry_pack_reverse(uint16_t rtc_status, uint8_t sample_type,
                           const SensorReading *readings, uint8_t count,
                           uint32_t tx_moment_ms, uint8_t *out_buf, size_t max_len) {
    if (!readings || !out_buf || count == 0) return -1;
    
    size_t needed = sizeof(PacketHeader) + count * (sizeof(uint16_t) + sizeof(int16_t));
    if (max_len < needed) return -2;

    PacketHeader hdr;
    hdr.magic = TELEM_MAGIC;
    hdr.version = TELEM_VERSION;
    hdr.flags = (MODE_REVERSE_DELTA & 0x03) | (rtc_status & 0x0C);
    hdr.sample_count = count;
    hdr.sample_type = sample_type;
    hdr.anchor_sec = 0; // Не потрібен для зворотних дельт

    memcpy(out_buf, &hdr, sizeof(hdr));
    uint8_t *ptr = out_buf + sizeof(hdr);

    // 1. Запис масиву зворотних дельт (у мілісекундах)
    for (uint8_t i = 0; i < count; ++i) {
        uint32_t diff = tx_moment_ms - readings[i].local_time_ms;
        uint16_t delta16 = (diff > 65535) ? 65535 : (uint16_t)diff;
        memcpy(ptr, &delta16, sizeof(uint16_t));
        ptr += sizeof(uint16_t);
    }

    // 2. Запис масиву корисних даних сенсора
    for (uint8_t i = 0; i < count; ++i) {
        memcpy(ptr, &readings[i].sensor_raw, sizeof(int16_t));
        ptr += sizeof(int16_t);
    }

    return (int)(ptr - out_buf);
}

// Реконструкція абсолютних часових міток на стороні сервера
int telemetry_unpack_reconstruct(const uint8_t *in_buf, size_t len,
                                 uint64_t server_rx_utc_ms, uint32_t prop_delay_ms,
                                 DecodedPoint *out_points, uint8_t max_points) {
    if (!in_buf || !out_points || len < sizeof(PacketHeader)) return -1;

    PacketHeader hdr;
    memcpy(&hdr, in_buf, sizeof(hdr));
    if (hdr.magic != TELEM_MAGIC || hdr.version != TELEM_VERSION) return -2;
    if (hdr.sample_count > max_points) return -3;

    size_t expected_len = sizeof(PacketHeader) + hdr.sample_count * (sizeof(uint16_t) + sizeof(int16_t));
    if (len < expected_len) return -4;

    uint8_t mode = hdr.flags & 0x03;
    const uint8_t *delta_ptr = in_buf + sizeof(PacketHeader);
    const uint8_t *val_ptr = delta_ptr + hdr.sample_count * sizeof(uint16_t);

    if (mode == MODE_REVERSE_DELTA) {
        uint64_t anchor_utc_ms = server_rx_utc_ms - prop_delay_ms;
        for (uint8_t i = 0; i < hdr.sample_count; ++i) {
            uint16_t delta_ms;
            int16_t raw_val;
            memcpy(&delta_ms, delta_ptr + i * sizeof(uint16_t), sizeof(uint16_t));
            memcpy(&raw_val, val_ptr + i * sizeof(int16_t), sizeof(int16_t));

            out_points[i].timestamp_utc_ms = anchor_utc_ms - delta_ms;
            out_points[i].sensor_raw = raw_val;
        }
        return hdr.sample_count;
    }

    return -5; // Інші режими обробляються окремо
}
