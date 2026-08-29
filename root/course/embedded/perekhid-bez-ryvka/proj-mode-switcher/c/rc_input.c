#include "rc_input.h"

#include <math.h>

/* CRC8/DVB-S2, поліном 0xD5 — саме такий у CRSF. */
uint8_t rc_crc8(const uint8_t *data, size_t len)
{
    uint8_t crc = 0;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b)
            crc = (crc & 0x80u) ? (uint8_t)((crc << 1) ^ 0xD5u)
                                : (uint8_t)(crc << 1);
    }
    return crc;
}

rc_err_t rc_frame_parse(const uint8_t *frame, size_t len, rc_channels_t *out)
{
    if (!frame || !out || len < RC_FRAME_SIZE) return RC_ERR_SHORT;
    if (frame[0] != RC_ADDR_FC)                return RC_ERR_ADDR;
    if (frame[1] != RC_PAYLOAD_LEN)            return RC_ERR_LEN;
    if (frame[2] != RC_TYPE_CHANNELS)          return RC_ERR_TYPE;
    /* CRC рахується від байта типу до останнього байта даних. */
    if (rc_crc8(&frame[2], 23) != frame[25])   return RC_ERR_CRC;

    const uint8_t *p = &frame[3];
    uint32_t acc = 0;
    int bits = 0;
    size_t bi = 0;
    for (int c = 0; c < RC_CHANNEL_COUNT; ++c) {
        /* 16 каналів по 11 біт, молодшими бітами вперед */
        while (bits < 11) { acc |= (uint32_t)p[bi++] << bits; bits += 8; }
        out->ch[c] = (uint16_t)(acc & 0x7FFu);
        acc >>= 11;
        bits -= 11;
    }
    return RC_OK;
}

void rc_frame_build(const rc_channels_t *ch, uint8_t frame[RC_FRAME_SIZE])
{
    frame[0] = (uint8_t)RC_ADDR_FC;
    frame[1] = (uint8_t)RC_PAYLOAD_LEN;
    frame[2] = (uint8_t)RC_TYPE_CHANNELS;

    uint8_t *p = &frame[3];
    uint32_t acc = 0;
    int bits = 0;
    size_t bi = 0;
    for (int c = 0; c < RC_CHANNEL_COUNT; ++c) {
        acc |= (uint32_t)(ch->ch[c] & 0x7FFu) << bits;
        bits += 11;
        while (bits >= 8) { p[bi++] = (uint8_t)(acc & 0xFFu); acc >>= 8; bits -= 8; }
    }
    frame[25] = rc_crc8(&frame[2], 23);
}

/* Шкала CRSF: 172 ≈ 988 мкс, 1811 ≈ 2012 мкс. */
float rc_channel_us(uint16_t raw)
{
    return 0.62477f * (float)raw + 881.0f;
}

float rc_channel_unit(uint16_t raw)
{
    float u = (rc_channel_us(raw) - 988.0f) / 1024.0f;
    if (u < 0.0f) u = 0.0f;
    if (u > 1.0f) u = 1.0f;
    /* Крок кванта ≈0.06 %; округлюємо до 0.1 %, щоб останній біт не дрижав. */
    return roundf(u * 1000.0f) / 1000.0f;
}

int rc_switch_pos(float us, int prev_pos)
{
    const float lo = 1300.0f, hi = 1700.0f, hyst = 40.0f;
    /* Гістерезис: на межі позиція не має мерехтіти від шуму лінка. */
    if (prev_pos == 0) {
        if (us > hi + hyst) return 2;
        if (us > lo + hyst) return 1;
        return 0;
    }
    if (prev_pos == 2) {
        if (us < lo - hyst) return 0;
        if (us < hi - hyst) return 1;
        return 2;
    }
    if (us > hi + hyst) return 2;
    if (us < lo - hyst) return 0;
    return 1;
}

void rc_link_init(rc_link_t *l, uint32_t now_ms)
{
    for (int i = 0; i < RC_CHANNEL_COUNT; ++i) l->ch.ch[i] = 992;
    l->last_ok_ms = now_ms;
    l->have_data = false;
    l->failsafe = true;      /* доки жодного кадру не прийшло — довіри лінку нема */
    l->frames_ok = 0;
    l->crc_errors = 0;
    l->format_errors = 0;
}

rc_err_t rc_link_feed(rc_link_t *l, const uint8_t *frame, size_t len, uint32_t now_ms)
{
    rc_channels_t ch;
    const rc_err_t e = rc_frame_parse(frame, len, &ch);
    if (e != RC_OK) {
        /* Побитий кадр не оновлює ні канали, ні таймер: інакше шум на лінії
           тримав би failsafe вимкненим при мертвому передавачі. */
        if (e == RC_ERR_CRC) l->crc_errors++;
        else                 l->format_errors++;
        return e;
    }
    l->ch = ch;
    l->last_ok_ms = now_ms;
    l->have_data = true;
    l->failsafe = false;
    l->frames_ok++;
    return RC_OK;
}

bool rc_link_tick(rc_link_t *l, uint32_t now_ms)
{
    l->failsafe = !l->have_data || (now_ms - l->last_ok_ms > RC_FAILSAFE_MS);
    return l->failsafe;
}
