#include "mission.h"

#include <math.h>
#include <stddef.h>
#include <string.h>

#define FM_EARTH_RADIUS_M 6371000.0
#define FM_DEG_TO_RAD     0.017453292519943295

void fm_mission_clear(fm_mission_t *m)
{
    if (!m) {
        return;
    }
    memset(m, 0, sizeof(*m));
}

bool fm_mission_append(fm_mission_t *m, const fm_mission_item_t *item)
{
    if (!m || !item || m->count >= FM_MISSION_MAX_ITEMS) {
        return false;
    }
    m->items[m->count++] = *item;
    return true;
}

static void crc_accumulate(uint16_t *crc, uint8_t byte)
{
    /* CRC-16/CCITT-FALSE: поліном 0x1021, початкове значення 0xFFFF. */
    *crc ^= (uint16_t)((uint16_t)byte << 8);
    for (int bit = 0; bit < 8; ++bit) {
        *crc = (uint16_t)((*crc & 0x8000u) ? ((*crc << 1) ^ 0x1021u) : (*crc << 1));
    }
}

static void crc_field(uint16_t *crc, const void *field, size_t len)
{
    const uint8_t *bytes = (const uint8_t *)field;

    for (size_t i = 0; i < len; ++i) {
        crc_accumulate(crc, bytes[i]);
    }
}

uint16_t fm_mission_crc(const fm_mission_t *m)
{
    uint16_t crc = 0xFFFFu;

    if (!m) {
        return crc;
    }
    for (uint16_t i = 0; i < m->count; ++i) {
        const fm_mission_item_t *it = &m->items[i];

        /* Байти беремо полями, а не одним sizeof(struct): вирівнювання лишає в
           структурі дірки, вміст яких у різних збірках різний — сума б пливла. */
        crc_field(&crc, &it->lat_1e7,   sizeof(it->lat_1e7));
        crc_field(&crc, &it->lon_1e7,   sizeof(it->lon_1e7));
        crc_field(&crc, &it->alt_rel_m, sizeof(it->alt_rel_m));
        crc_field(&crc, &it->command,   sizeof(it->command));
    }
    return crc;
}

void fm_geo_offset_m(int32_t lat_a_1e7, int32_t lon_a_1e7,
                     int32_t lat_b_1e7, int32_t lon_b_1e7,
                     float *north_m, float *east_m)
{
    const double lat_a = (double)lat_a_1e7 * 1e-7;
    const double lat_b = (double)lat_b_1e7 * 1e-7;
    const double d_lat = (lat_b - lat_a) * FM_DEG_TO_RAD;
    /* Довжина градуса довготи стискається косинусом широти — без цього множника
       план у Скандинавії проходив би геозону, якої фактично не проходить. */
    const double d_lon = ((double)(lon_b_1e7 - lon_a_1e7) * 1e-7) * FM_DEG_TO_RAD
                       * cos(0.5 * (lat_a + lat_b) * FM_DEG_TO_RAD);

    if (north_m) {
        *north_m = (float)(d_lat * FM_EARTH_RADIUS_M);
    }
    if (east_m) {
        *east_m = (float)(d_lon * FM_EARTH_RADIUS_M);
    }
}

float fm_geo_distance_m(int32_t lat_a_1e7, int32_t lon_a_1e7,
                        int32_t lat_b_1e7, int32_t lon_b_1e7)
{
    float north = 0.0f;
    float east  = 0.0f;

    fm_geo_offset_m(lat_a_1e7, lon_a_1e7, lat_b_1e7, lon_b_1e7, &north, &east);
    return sqrtf(north * north + east * east);
}

fm_mission_status_t fm_mission_validate(const fm_mission_t *m,
                                        int32_t home_lat_1e7, int32_t home_lon_1e7,
                                        float fence_radius_m, float max_alt_m)
{
    if (!m || m->count == 0) {
        return FM_MISSION_EMPTY;
    }
    if (fm_mission_crc(m) != m->stored_crc) {
        return FM_MISSION_CRC_MISMATCH;
    }

    for (uint16_t i = 0; i < m->count; ++i) {
        const fm_mission_item_t *it = &m->items[i];

        if (it->command == 0) {
            return FM_MISSION_BAD_COMMAND;
        }
        if (isnan(it->alt_rel_m) || it->alt_rel_m <= 0.0f || it->alt_rel_m > max_alt_m) {
            return FM_MISSION_BAD_ALTITUDE;
        }
        if (it->lat_1e7 == 0 && it->lon_1e7 == 0) {
            /* Нульова координата — типовий слід недоотриманого пакета плану. */
            return FM_MISSION_OUT_OF_FENCE;
        }
        if (fm_geo_distance_m(home_lat_1e7, home_lon_1e7,
                              it->lat_1e7, it->lon_1e7) > fence_radius_m) {
            return FM_MISSION_OUT_OF_FENCE;
        }
    }
    return FM_MISSION_OK;
}

const char *fm_mission_status_text(fm_mission_status_t st)
{
    switch (st) {
    case FM_MISSION_OK:           return "mission valid";
    case FM_MISSION_EMPTY:        return "mission empty";
    case FM_MISSION_CRC_MISMATCH: return "mission CRC mismatch";
    case FM_MISSION_BAD_ALTITUDE: return "mission altitude out of range";
    case FM_MISSION_OUT_OF_FENCE: return "waypoint outside fence";
    case FM_MISSION_BAD_COMMAND:  return "unknown mission command";
    default:                      return "mission state unknown";
    }
}
