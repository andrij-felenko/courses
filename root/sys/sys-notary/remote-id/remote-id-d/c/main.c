#include <stdint.h>
#include <string.h>
#include <math.h>

#pragma pack(push, 1)

typedef struct {
    uint8_t  header;             /* 0x11: Msg Type 0x1, Version 0x1 */
    uint8_t  status_flags;       /* Біти 7..4: статус польоту (2 = Airborne) */
    uint8_t  direction;          /* 0..359 град */
    uint8_t  speed_h;            /* крок 0.25 м/с */
    int8_t   speed_v;            /* крок 0.5 м/с зі знаком */
    int32_t  lat;                /* grad * 1e7 */
    int32_t  lon;                /* grad * 1e7 */
    uint16_t alt_geodetic;       /* (alt_m + 1000) / 0.5 */
    uint16_t alt_pressure;       /* (alt_m + 1000) / 0.5 */
    uint16_t height_agl;         /* AGL / 0.5 */
    uint8_t  accuracy_horiz_vert;/* HAcc (4b) | VAcc (4b) */
    uint8_t  accuracy_baro_speed;/* BaroAcc (4b) | SpeedAcc (4b) */
    uint16_t timestamp_tenths;   /* 0.1 с поточної години */
    uint8_t  time_adv_acc;
    uint8_t  reserved;
} odid_location_msg_t;

#pragma pack(pop)

void encode_location_frame(odid_location_msg_t *msg, double lat, double lon, 
                           double alt_wgs84, double spd_h, double spd_v, 
                           double hdg, uint32_t sec_in_hour, uint32_t ms) {
    memset(msg, 0, sizeof(odid_location_msg_t));
    msg->header = (0x1 << 4) | 0x01;
    msg->status_flags = (2 << 4); /* Airborne */
    
    int deg = (int)round(hdg);
    msg->direction = (uint8_t)((deg >= 0 ? deg : deg + 360) % 360);
    
    msg->speed_h = (uint8_t)fmin(spd_h / 0.25, 254.0);
    msg->speed_v = (int8_t)fmax(-127.0, fmin(spd_v / 0.5, 127.0));
    
    msg->lat = (int32_t)round(lat * 10000000.0);
    msg->lon = (int32_t)round(lon * 10000000.0);
    
    double enc_alt = (alt_wgs84 + 1000.0) / 0.5;
    msg->alt_geodetic = (uint16_t)(enc_alt < 0 ? 0 : (enc_alt > 65535 ? 65535 : enc_alt));
    msg->alt_pressure = msg->alt_geodetic;
    
    msg->accuracy_horiz_vert = (11 << 4) | (10 & 0x0F); /* HAcc < 3m, VAcc < 10m */
    msg->accuracy_baro_speed = (10 << 4) | (10 & 0x0F);
    
    msg->timestamp_tenths = (uint16_t)(((sec_in_hour % 3600) * 10 + (ms / 100)) % 36000);
}
