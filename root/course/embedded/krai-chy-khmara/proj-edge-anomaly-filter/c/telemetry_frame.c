#include "telemetry_frame.h"

#include <math.h>
#include <string.h>

#define FRAME_MAGIC    0x7Eu
#define FRAME_VERSION  1u

uint16_t telemetry_crc16(const uint8_t *data, size_t len)
{
    /* CRC-16/CCITT-FALSE: поліном 0x1021, початок 0xFFFF, без відображення.
       Побітово — таблиця на 512 байт тут не окупається: кадр менший за 90 байт,
       а ПЗП на дрібному МК дорожче за такти. */
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

static void put_u8(uint8_t *buf, size_t *pos, uint8_t v)
{
    buf[(*pos)++] = v;
}

static void put_u16(uint8_t *buf, size_t *pos, uint16_t v)
{
    buf[(*pos)++] = (uint8_t)(v & 0xFFu);
    buf[(*pos)++] = (uint8_t)(v >> 8);
}

static void put_u32(uint8_t *buf, size_t *pos, uint32_t v)
{
    buf[(*pos)++] = (uint8_t)(v & 0xFFu);
    buf[(*pos)++] = (uint8_t)((v >> 8) & 0xFFu);
    buf[(*pos)++] = (uint8_t)((v >> 16) & 0xFFu);
    buf[(*pos)++] = (uint8_t)((v >> 24) & 0xFFu);
}

static void put_f32(uint8_t *buf, size_t *pos, float v)
{
    /* Не-скінченне значення в ефір не пускаємо: розбирач на тому боці
       майже напевно впаде на ньому, а прапорець відмови вже в заголовку. */
    if (!isfinite(v)) {
        v = 0.0f;
    }
    uint32_t bits;
    memcpy(&bits, &v, sizeof(bits));   /* єдиний законний спосіб глянути на біти float */
    put_u32(buf, pos, bits);
}

static uint16_t z_to_q8_8(float z)
{
    if (!isfinite(z) || z >= 255.99f) {
        return 0xFFFFu;               /* насичення: «дуже далеко», точність тут не потрібна */
    }
    if (z <= 0.0f) {
        return 0u;
    }
    return (uint16_t)(z * 256.0f + 0.5f);
}

static int16_t sample_to_fixed(float sample, float mean)
{
    if (!isfinite(sample) || !isfinite(mean)) {
        return TELEMETRY_SNAPSHOT_INVALID;
    }
    const float scaled = (sample - mean) * 100.0f;
    if (scaled >= 32767.0f) {
        return 32767;
    }
    if (scaled <= -32767.0f) {
        return -32767;                /* -32768 зарезервовано під «невалідна» */
    }
    return (int16_t)(scaled >= 0.0f ? scaled + 0.5f : scaled - 0.5f);
}

size_t telemetry_frame_encode(const telemetry_report_t *report,
                              const float *snapshot,
                              uint32_t snapshot_len,
                              uint8_t *out,
                              size_t out_cap)
{
    if (report == NULL || out == NULL) {
        return 0u;
    }
    if (snapshot == NULL) {
        snapshot_len = 0u;
    }
    if (snapshot_len > RING_BUFFER_CAPACITY) {
        snapshot_len = RING_BUFFER_CAPACITY;
    }

    const size_t need = 22u + 2u * (size_t)snapshot_len + 2u;
    if (out_cap < need) {
        return 0u;                    /* краще нуль, ніж кадр, обрізаний посередині */
    }

    size_t pos = 0;
    put_u8(out, &pos, FRAME_MAGIC);
    put_u8(out, &pos, (uint8_t)((FRAME_VERSION << 4) | (report->sensor_fault ? 0x1u : 0x0u)));
    put_u8(out, &pos, (uint8_t)report->action);
    put_u32(out, &pos, report->timestamp_ms);
    put_f32(out, &pos, report->value);
    put_f32(out, &pos, report->running_mean);
    put_f32(out, &pos, report->running_stddev);
    put_u16(out, &pos, z_to_q8_8(report->z_score));
    put_u8(out, &pos, (uint8_t)snapshot_len);

    for (uint32_t i = 0; i < snapshot_len; ++i) {
        put_u16(out, &pos, (uint16_t)sample_to_fixed(snapshot[i], report->running_mean));
    }

    put_u16(out, &pos, telemetry_crc16(out, pos));
    return pos;
}
