#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define TELEMETRY_MAGIC 0x7E
#define TELEMETRY_VERSION 0x01

#define TIME_MODE_MASK        0x0003
#define TIME_MODE_ABS         0x0000
#define TIME_MODE_FWD_DELTA   0x0001
#define TIME_MODE_REV_ANCHOR  0x0002
#define TIME_MODE_PERIODIC    0x0003

#define RTC_STATUS_MASK       0x001C
#define RTC_STATUS_UNSYNC     0x0000
#define RTC_STATUS_ESTIMATED  0x0004
#define RTC_STATUS_NTP        0x0008
#define RTC_STATUS_GNSS       0x000C

#define DELTA_SCALE_MASK      0x0060
#define DELTA_SCALE_MS        0x0000
#define DELTA_SCALE_100MS     0x0020
#define DELTA_SCALE_SEC       0x0040

#define TELEM_OK               0
#define TELEM_ERR_NULL_PTR    -1
#define TELEM_ERR_BUF_OVERFLOW -2
#define TELEM_ERR_BAD_MAGIC   -3
#define TELEM_ERR_BAD_VERSION -4
#define TELEM_ERR_BAD_CRC     -5
#define TELEM_ERR_UNSUPPORTED -6

#pragma pack(push, 1)
typedef struct {
    uint8_t magic;
    uint8_t version;
    uint16_t flags;
    uint8_t sample_count;
    uint8_t sample_type;
    uint32_t anchor_seconds; // Опційно, 0 якщо MODE_REVERSE_ANCHOR
} TelemetryHeader;
#pragma pack(pop)

typedef struct {
    uint32_t delta_ms; // Зсув у мілісекундах
    int16_t value_raw; // Сире значення сенсора
} TelemetrySample;

// Упакувати серію вимірів у буфер передачі
int telemetry_pack_reverse_delta(
    uint16_t rtc_status_flag,
    uint8_t sample_type,
    const TelemetrySample *samples,
    uint8_t sample_count,
    uint8_t *out_buffer,
    size_t buffer_size
);

// Розпакувати та відновити абсолютні часові мітки на стороні сервера
int telemetry_unpack_reconstruct(
    const uint8_t *in_buffer,
    size_t in_size,
    uint64_t server_anchor_utc_ms,
    TelemetrySample *out_samples,
    uint64_t *out_timestamps_utc_ms,
    uint8_t max_samples
);
