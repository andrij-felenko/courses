#ifndef LINK_H
#define LINK_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Обидва напрямки — кадр фіксованої довжини 14 байтів. Фіксована довжина
// потрібна не заради краси: у FLRC вона економить заголовок і дає обом
// сторонам однаковий час у ефірі.
#define FRAME_LEN     14
#define UPLINK_SYNC   0x5A
#define DOWNLINK_SYNC 0xA5

#define FLAG_ARMED     0x01
#define FLAG_RATE_HIGH 0x02
#define FLAG_PAYLOAD   0x04
#define FLAG_FAILSAFE  0x08

typedef struct {
    uint8_t  sequence;
    uint16_t vbat_mv;       // напруга акумулятора апарата
    uint16_t current_da;    // струм апарата, десяті ампера
    int8_t   rssi_air_dbm;  // як апарат чує пульт
    uint8_t  link_pct;      // якість каналу за оцінкою апарата
    uint8_t  mos_temp_c;    // температура силових ключів
    uint8_t  flight_mode;
    uint8_t  sats;
    uint8_t  status;
} telemetry_t;

// Ковзне вікно на 64 слоти: скільки відповідей прийшло на останні 64 посилки.
typedef struct {
    uint64_t window;
    uint8_t  filled;
    uint8_t  lq_pct;
} link_stats_t;

uint16_t link_crc16(const uint8_t *data, size_t len);
void link_build_uplink(uint8_t out[FRAME_LEN], const uint16_t axes[HAL_ADC_AXES],
                       uint16_t switches, uint8_t flags, uint8_t aux);
bool link_parse_downlink(const uint8_t *in, size_t len, telemetry_t *out);
void link_stats_mark(link_stats_t *stats, bool received);

#endif
