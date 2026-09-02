#include "link.h"

#include <string.h>

#include "hal.h"

// CRC-16/CCITT-FALSE півбайтною таблицею: 32 байти флеш замість 512 і
// приблизно 3 мкс на кадр — у бюджет 15 мкс лягає з запасом.
static const uint16_t s_crc_tab[16] = {
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
    0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF
};

uint16_t link_crc16(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc = (uint16_t)((crc << 4) ^ s_crc_tab[((crc >> 12) ^ (data[i] >> 4)) & 0x0F]);
        crc = (uint16_t)((crc << 4) ^ s_crc_tab[((crc >> 12) ^ (data[i] & 0x0F)) & 0x0F]);
    }
    return crc;
}

// Пише n молодших бітів значення, починаючи з поточної бітової позиції.
static void put_bits(uint8_t *dst, size_t *bit, uint32_t value, uint8_t n)
{
    for (uint8_t i = 0; i < n; i++) {
        if (value & (1u << i)) {
            dst[*bit >> 3] |= (uint8_t)(1u << (*bit & 7u));
        }
        (*bit)++;
    }
}

void link_build_uplink(uint8_t out[FRAME_LEN], const uint16_t axes[HAL_ADC_AXES],
                       uint16_t switches, uint8_t flags, uint8_t aux)
{
    static uint8_t sequence;

    memset(out, 0, FRAME_LEN);
    out[0] = UPLINK_SYNC;
    out[1] = sequence++;

    // Чотири одинадцятибітні осі — це 44 біти; вони лягають у байти 2..7,
    // чотири останні біти лишаються нулями під майбутній п'ятий канал.
    size_t bit = 16;
    for (uint8_t i = 0; i < HAL_ADC_AXES; i++) {
        put_bits(out, &bit, axes[i] & 0x07FFu, 11);
    }

    out[8]  = (uint8_t)(switches & 0xFF);
    out[9]  = (uint8_t)(switches >> 8);
    out[10] = flags;
    out[11] = aux;

    uint16_t crc = link_crc16(out, FRAME_LEN - 2);
    out[12] = (uint8_t)(crc >> 8);
    out[13] = (uint8_t)crc;
}

bool link_parse_downlink(const uint8_t *in, size_t len, telemetry_t *out)
{
    if (len != FRAME_LEN || in[0] != DOWNLINK_SYNC) {
        return false;
    }
    uint16_t crc = link_crc16(in, FRAME_LEN - 2);
    if (crc != (uint16_t)(((uint16_t)in[12] << 8) | in[13])) {
        return false;
    }

    out->sequence     = in[1];
    out->vbat_mv      = (uint16_t)(in[2] | ((uint16_t)in[3] << 8));
    out->current_da   = (uint16_t)(in[4] | ((uint16_t)in[5] << 8));
    out->rssi_air_dbm = (int8_t)(-(int)in[6]);   // у кадрі їде модуль
    out->link_pct     = in[7] > 100 ? 100 : in[7];
    out->mos_temp_c   = in[8];
    out->flight_mode  = in[9];
    out->sats         = in[10];
    out->status       = in[11];
    return true;
}

void link_stats_mark(link_stats_t *stats, bool received)
{
    stats->window = (stats->window << 1) | (received ? 1u : 0u);
    if (stats->filled < 64) {
        stats->filled++;
    }

    uint8_t got = 0;
    uint64_t w = stats->window;
    while (w) {
        got = (uint8_t)(got + (w & 1u));
        w >>= 1;
    }
    stats->lq_pct = (uint8_t)((got * 100u) / stats->filled);
}
