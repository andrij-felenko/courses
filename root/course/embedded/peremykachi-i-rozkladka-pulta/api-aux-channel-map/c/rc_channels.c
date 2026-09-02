#include "rc_channels.h"

#include <math.h>
#include <string.h>

/* Рядок — розкладка, стовпець — вісь (ROLL, PITCH, YAW, THROTTLE);
   значення — номер каналу на дроті, з нуля. */
static const uint8_t k_map_table[RC_MAP_COUNT][RC_AXIS_COUNT] = {
    { 0, 1, 3, 2 },  /* AETR: крен, тангаж, газ, рискання */
    { 1, 2, 3, 0 },  /* TAER: газ, крен, тангаж, рискання */
    { 3, 1, 0, 2 },  /* RETA: рискання, тангаж, газ, крен */
    { 2, 0, 3, 1 },  /* ETAR: тангаж, газ, крен, рискання */
};

static const char *const k_map_names[RC_MAP_COUNT] = { "AETR", "TAER", "RETA", "ETAR" };

uint16_t rc_raw_to_us(uint16_t raw)
{
    if (raw <= RC_RAW_MIN) {
        return RC_US_MIN;
    }
    if (raw >= RC_RAW_MAX) {
        return RC_US_MAX;
    }
    /* T_us = 988 + (raw - 172) * 1024 / 1640; +820 — округлення вгору від половини */
    uint32_t num = (uint32_t)(raw - RC_RAW_MIN) * 1024U;
    return (uint16_t)(RC_US_MIN + (num + 820U) / 1640U);
}

uint16_t rc_us_to_raw(uint16_t us)
{
    if (us <= RC_US_MIN) {
        return RC_RAW_MIN;
    }
    if (us >= RC_US_MAX) {
        return RC_RAW_MAX;
    }
    uint32_t num = (uint32_t)(us - RC_US_MIN) * 1640U;
    return (uint16_t)(RC_RAW_MIN + (num + 512U) / 1024U);
}

void rc_unpack_11bit(const uint8_t payload[RC_PACKED_BYTES], uint16_t raw[RC_TOTAL_CHANNELS])
{
    if (payload == NULL || raw == NULL) {
        return;
    }

    for (unsigned i = 0; i < RC_TOTAL_CHANNELS; ++i) {
        unsigned bit   = i * 11U;
        unsigned byte  = bit >> 3;
        unsigned shift = bit & 7U;

        /* Канал ніколи не перетинає більш ніж три байти; третій беремо лише
           тоді, коли він справді існує в 22-байтовому полі. */
        uint32_t acc = (uint32_t)payload[byte] | ((uint32_t)payload[byte + 1U] << 8);
        if (byte + 2U < RC_PACKED_BYTES) {
            acc |= (uint32_t)payload[byte + 2U] << 16;
        }
        raw[i] = (uint16_t)((acc >> shift) & 0x07FFU);
    }
}

void rc_pack_11bit(const uint16_t raw[RC_TOTAL_CHANNELS], uint8_t payload[RC_PACKED_BYTES])
{
    if (payload == NULL || raw == NULL) {
        return;
    }
    memset(payload, 0, RC_PACKED_BYTES);

    for (unsigned i = 0; i < RC_TOTAL_CHANNELS; ++i) {
        uint32_t v     = (uint32_t)raw[i] & 0x07FFU;
        unsigned bit   = i * 11U;
        unsigned byte  = bit >> 3;
        unsigned shift = bit & 7U;

        payload[byte]      |= (uint8_t)(v << shift);
        payload[byte + 1U] |= (uint8_t)(v >> (8U - shift));
        if (shift > 5U && byte + 2U < RC_PACKED_BYTES) {
            payload[byte + 2U] |= (uint8_t)(v >> (16U - shift));
        }
    }
}

uint8_t rc_map_channel_index(rc_channel_map_t map, rc_axis_t axis)
{
    if ((unsigned)map >= RC_MAP_COUNT || (unsigned)axis >= RC_AXIS_COUNT) {
        return 0U;
    }
    return k_map_table[map][axis];
}

const char *rc_map_name(rc_channel_map_t map)
{
    return ((unsigned)map < RC_MAP_COUNT) ? k_map_names[map] : "?";
}

bool rc_apply_map(rc_channel_map_t map,
                  const uint16_t channels_us[RC_TOTAL_CHANNELS],
                  uint16_t axes_us[RC_AXIS_COUNT])
{
    if ((unsigned)map >= RC_MAP_COUNT || channels_us == NULL || axes_us == NULL) {
        return false;
    }
    for (unsigned axis = 0; axis < RC_AXIS_COUNT; ++axis) {
        axes_us[axis] = channels_us[k_map_table[map][axis]];
    }
    return true;
}

uint16_t rc_apply_deadband(uint16_t us, uint16_t deadband_us)
{
    int32_t delta = (int32_t)us - (int32_t)RC_US_CENTER;
    int32_t db    = (int32_t)deadband_us;

    if (delta > -db && delta < db) {
        return RC_US_CENTER;
    }
    /* Зсув, а не обнулення: на межі зони немає розриву команди */
    delta += (delta > 0) ? -db : db;
    return (uint16_t)((int32_t)RC_US_CENTER + delta);
}

void rc_biquad_init(rc_biquad_t *f, float cutoff_hz, float sample_hz)
{
    if (f == NULL) {
        return;
    }
    memset(f, 0, sizeof(*f));

    /* Виродження — фільтр стає прямим проводом, а не джерелом NaN */
    if (sample_hz <= 0.0f || cutoff_hz <= 0.0f || cutoff_hz >= sample_hz * 0.5f) {
        f->b0 = 1.0f;
        return;
    }

    const float q     = 0.70710678f;             /* Баттерворт, 2-й порядок */
    const float omega = 2.0f * 3.14159265f * cutoff_hz / sample_hz;
    const float cs    = cosf(omega);
    const float alpha = sinf(omega) / (2.0f * q);

    const float a0 = 1.0f + alpha;
    f->b0 = ((1.0f - cs) * 0.5f) / a0;
    f->b1 = (1.0f - cs) / a0;
    f->b2 = f->b0;
    f->a1 = (-2.0f * cs) / a0;
    f->a2 = (1.0f - alpha) / a0;
}

float rc_biquad_apply(rc_biquad_t *f, float x)
{
    if (f == NULL) {
        return x;
    }
    if (!f->primed) {
        /* Перший кадр заповнює лінію затримки, інакше фільтр «виповзає» з нуля */
        f->x1 = f->x2 = x;
        f->y1 = f->y2 = x;
        f->primed = true;
        return x;
    }

    float y = f->b0 * x + f->b1 * f->x1 + f->b2 * f->x2 - f->a1 * f->y1 - f->a2 * f->y2;

    f->x2 = f->x1;
    f->x1 = x;
    f->y2 = f->y1;
    f->y1 = y;
    return y;
}
