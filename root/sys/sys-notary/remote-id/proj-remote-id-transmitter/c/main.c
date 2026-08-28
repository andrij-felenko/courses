#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#pragma pack(push, 1)

#define ODID_MSG_SIZE 25
#define ODID_PROTOCOL_VERSION 0x01

typedef enum {
    ODID_MSG_TYPE_BASIC_ID   = 0x0,
    ODID_MSG_TYPE_LOCATION   = 0x1,
    ODID_MSG_TYPE_AUTH       = 0x2,
    ODID_MSG_TYPE_SELF_ID    = 0x3,
    ODID_MSG_TYPE_SYSTEM     = 0x4,
    ODID_MSG_TYPE_OPERATOR   = 0x5,
    ODID_MSG_TYPE_PACK       = 0xF
} odid_msg_type_t;

typedef enum {
    ODID_ID_TYPE_SERIAL_NUMBER = 1,
    ODID_ID_TYPE_CAA           = 2,
    ODID_ID_TYPE_SESSION_ID    = 4
} odid_id_type_t;

typedef enum {
    ODID_UA_TYPE_AEROPLANE   = 1,
    ODID_UA_TYPE_HELICOPTER  = 2,
    ODID_UA_TYPE_MULTIROTOR  = 15
} odid_ua_type_t;

typedef enum {
    ODID_STATUS_UNDECLARED = 0,
    ODID_STATUS_GROUND     = 1,
    ODID_STATUS_AIRBORNE   = 2,
    ODID_STATUS_EMERGENCY  = 3
} odid_status_t;

/* Структура 0x0: Basic ID (25 байтів) */
typedef struct {
    uint8_t header;             /* Старші 4 біти: 0x0, молодші: Protocol Version */
    uint8_t id_ua_type;         /* Старші 4 біти: id_type, молодші: ua_type */
    uint8_t uas_id[20];         /* ASCII рядок серійного номера ANSI/CTA-2063-A */
    uint8_t reserved[3];
} odid_basic_id_t;

/* Структура 0x1: Location/Vector (25 байтів) */
typedef struct {
    uint8_t header;             /* Старші 4 біти: 0x1, молодші: Protocol Version */
    uint8_t status_flags;       /* Старші 4 біти: Status (0..3) */
    uint8_t direction;          /* Напрямок руху 0..359 град (крок 1 град) */
    uint8_t speed_horizontal;   /* Швидкість horiz (крок 0.25 м/с) */
    int8_t  speed_vertical;     /* Швидкість vert (крок 0.5 м/с, зі знаком) */
    int32_t latitude;           /* Широта: grad * 1e7 */
    int32_t longitude;          /* Довгота: grad * 1e7 */
    uint16_t altitude_geodetic; /* Висота WGS84: (alt_m + 1000.0) / 0.5 */
    uint16_t altitude_pressure; /* Висота барометрична */
    uint16_t height_agl;        /* Висота над землею (AGL) */
    uint8_t horiz_vert_acc;     /* Старші 4 біти: HAcc (0..13), молодші: VAcc */
    uint8_t baro_speed_acc;     /* Старші 4 біти: BaroAcc, молодші: SpeedAcc */
    uint16_t timestamp;         /* Десяті частки секунди поточної години (0..35999) */
    uint8_t time_adv_acc;       /* Точність часу та інтервал */
    uint8_t reserved;
} odid_location_t;

/* Структура 0x4: System Data (25 байтів) */
typedef struct {
    uint8_t header;             /* Старші 4 біти: 0x4, молодші: Protocol Version */
    uint8_t operator_loc_type;  /* 0 = Takeoff, 1 = Live GNSS, 2 = Fixed */
    int32_t operator_latitude;  /* Широта оператора: grad * 1e7 */
    int32_t operator_longitude; /* Довгота оператора: grad * 1e7 */
    uint16_t area_count;        /* Кількість БПЛА в групі */
    uint8_t area_radius;        /* Радіус зони: крок 10 м */
    uint16_t area_ceiling;      /* Верхня стеля зони */
    uint16_t area_floor;        /* Нижня підлога зони */
    uint8_t classification;     /* Категорія EASA Open/Specific */
    uint16_t operator_altitude; /* Геодезична висота оператора WGS84 */
    uint32_t system_timestamp;  /* UTC секунди Unix */
    uint8_t reserved;
} odid_system_t;

/* Структура 0xF: Message Pack (Об'єднання повідомлень) */
typedef struct {
    uint8_t header;             /* 0xF1 */
    uint8_t msg_pack_size;      /* Розмір одного елемента = 25 байтів */
    uint8_t msg_count;          /* Кількість вкладених повідомлень */
    uint8_t messages[3 * ODID_MSG_SIZE]; /* Basic ID + Location + System */
} odid_msg_pack_t;

#pragma pack(pop)

/* Кодування повідомлення Basic ID */
void odid_encode_basic_id(odid_basic_id_t *out, odid_id_type_t id_type, 
                          odid_ua_type_t ua_type, const char *serial_str) {
    memset(out, 0, sizeof(odid_basic_id_t));
    out->header = (ODID_MSG_TYPE_BASIC_ID << 4) | (ODID_PROTOCOL_VERSION & 0x0F);
    out->id_ua_type = ((id_type & 0x0F) << 4) | (ua_type & 0x0F);
    size_t len = strlen(serial_str);
    if (len > 20) len = 20;
    memcpy(out->uas_id, serial_str, len);
}

/* Кодування повідомлення Location */
void odid_encode_location(odid_location_t *out, odid_status_t status,
                          double lat_deg, double lon_deg, double alt_wgs84_m,
                          double speed_h_mps, double speed_v_mps, double heading_deg,
                          uint32_t sec_in_hour, uint32_t ms_fraction) {
    memset(out, 0, sizeof(odid_location_t));
    out->header = (ODID_MSG_TYPE_LOCATION << 4) | (ODID_PROTOCOL_VERSION & 0x0F);
    out->status_flags = (status & 0x0F) << 4;

    int hdg = (int)round(heading_deg);
    if (hdg < 0) hdg = (hdg % 360) + 360;
    out->direction = (uint8_t)(hdg % 360);

    out->speed_horizontal = (uint8_t)(fmin(speed_h_mps / 0.25, 254.0));
    out->speed_vertical = (int8_t)(fmax(-127.0, fmin(speed_v_mps / 0.5, 127.0)));

    out->latitude = (int32_t)round(lat_deg * 10000000.0);
    out->longitude = (int32_t)round(lon_deg * 10000000.0);

    double alt_enc = (alt_wgs84_m + 1000.0) / 0.5;
    if (alt_enc < 0.0) alt_enc = 0.0;
    if (alt_enc > 65535.0) alt_enc = 65535.0;
    out->altitude_geodetic = (uint16_t)round(alt_enc);
    out->altitude_pressure = out->altitude_geodetic;

    out->horiz_vert_acc = (11 << 4) | (10 & 0x0F);
    out->baro_speed_acc = (10 << 4) | (10 & 0x0F);

    uint32_t tenths = (sec_in_hour % 3600) * 10 + (ms_fraction / 100);
    out->timestamp = (uint16_t)(tenths % 36000);
    out->time_adv_acc = 0x10;
}

/* Формування пакету Bluetooth 4.2 Legacy Advertising (32 байти PDU) */
uint8_t odid_build_ble4_packet(uint8_t *out_pdu, const void *odid_msg) {
    out_pdu[0] = 0x02; /* Довжина секції Flags */
    out_pdu[1] = 0x01; /* AD Type = Flags */
    out_pdu[2] = 0x06; /* LE General Discoverable Mode */

    out_pdu[3] = 0x1B; /* Довжина секції Service Data: 1 + 2 + 25 = 28 байтів (0x1B) */
    out_pdu[4] = 0x16; /* AD Type = Service Data - 16-bit UUID */
    out_pdu[5] = 0xFA; /* OpenDroneID UUID: 0xFFFA (Little-endian) */
    out_pdu[6] = 0xFF;

    memcpy(&out_pdu[7], odid_msg, ODID_MSG_SIZE);
    return 32;
}
