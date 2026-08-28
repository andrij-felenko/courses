/* beacon_parser.h / beacon_parser.c — Стандарт C99/C11 */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#pragma pack(push, 1)

/* Структура AD-блоку загального призначення */
typedef struct {
    uint8_t length;
    uint8_t type;
    uint8_t data[29];
} ble_ad_element_t;

/* Двійковий кадр iBeacon (Apple) */
typedef struct {
    uint8_t  len;              /* 0x1A */
    uint8_t  type;             /* 0xFF */
    uint16_t company_id;       /* 0x004C (Little Endian) */
    uint8_t  beacon_type;      /* 0x02 */
    uint8_t  subtype_len;      /* 0x15 */
    uint8_t  uuid[16];         /* Proximity UUID (Big Endian) */
    uint16_t major;            /* Major (Big Endian) */
    uint16_t minor;            /* Minor (Big Endian) */
    int8_t   measured_power;   /* TxPower @ 1m */
} ibeacon_frame_t;

/* Двійковий кадр Eddystone-UID */
typedef struct {
    uint8_t  frame_type;       /* 0x00 */
    int8_t   tx_power_0m;      /* TxPower @ 0m */
    uint8_t  namespace_id[10];
    uint8_t  instance_id[6];
    uint16_t reserved;         /* 0x0000 */
} eddystone_uid_t;

/* Двійковий кадр Eddystone-TLM (незашифрований) */
typedef struct {
    uint8_t  frame_type;       /* 0x20 */
    uint8_t  version;          /* 0x00 */
    uint16_t vbatt_mv;         /* Напруга батареї (Big Endian) */
    int16_t  temp_fixed;       /* 8.8 fixed-point (Big Endian) */
    uint32_t adv_cnt;          /* Кількість пакетів (Big Endian) */
    uint32_t uptime_ticks;     /* Тики по 0.1 с (Big Endian) */
} eddystone_tlm_t;

/* Двійковий кадр AltBeacon */
typedef struct {
    uint8_t  len;              /* 0x1B */
    uint8_t  type;             /* 0xFF */
    uint16_t manufacturer_id;  /* Little Endian */
    uint16_t beacon_code;      /* 0xBEAC (Big Endian) */
    uint8_t  beacon_id[20];
    int8_t   ref_rssi;         /* Ref RSSI @ 1m */
    uint8_t  mfg_reserved;
} altbeacon_frame_t;

#pragma pack(pop)

/* Типи розпізнаних маячків */
typedef enum {
    BEACON_TYPE_UNKNOWN = 0,
    BEACON_TYPE_IBEACON,
    BEACON_TYPE_EDDYSTONE_UID,
    BEACON_TYPE_EDDYSTONE_URL,
    BEACON_TYPE_EDDYSTONE_TLM,
    BEACON_TYPE_ALTBEACON
} beacon_type_t;

/* Розпарсені дані маячка */
typedef struct {
    beacon_type_t type;
    int8_t   calibrated_power_1m; /* Зведений рівень до 1 метра */
    union {
        struct {
            uint8_t  uuid[16];
            uint16_t major;
            uint16_t minor;
        } ibeacon;
        struct {
            uint8_t namespace_id[10];
            uint8_t instance_id[6];
        } eddystone_uid;
        struct {
            char url[128];
        } eddystone_url;
        struct {
            uint16_t battery_mv;
            float    temperature_c;
            uint32_t adv_count;
            uint32_t uptime_sec;
        } eddystone_tlm;
        struct {
            uint16_t manufacturer_id;
            uint8_t  beacon_id[20];
        } altbeacon;
    } data;
} parsed_beacon_t;

/* 1D Фільтр Калмана */
typedef struct {
    float x; /* Оцінка стану RSSI */
    float p; /* Дисперсія оцінки */
    float q; /* Коваріація шуму процесу */
    float r; /* Коваріація шуму вимірювача */
    bool  initialized;
} kalman_filter_t;

void kalman_init(kalman_filter_t *kf, float q, float r) {
    kf->x = 0.0f;
    kf->p = 5.0f;
    kf->q = q;
    kf->r = r;
    kf->initialized = false;
}

float kalman_update(kalman_filter_t *kf, float measurement) {
    if (!kf->initialized) {
        kf->x = measurement;
        kf->p = 5.0f;
        kf->initialized = true;
        return kf->x;
    }
    /* Прогноз */
    float p_pred = kf->p + kf->q;
    /* Оновлення */
    float k = p_pred / (p_pred + kf->r);
    kf->x = kf->x + k * (measurement - kf->x);
    kf->p = (1.0f - k) * p_pred;
    return kf->x;
}

/* Розрахунок відстані за моделлю Log-Distance Path Loss */
float calculate_distance(int8_t tx_power_1m, float rssi, float path_loss_exponent) {
    if (path_loss_exponent <= 0.0f) path_loss_exponent = 2.0f;
    float exponent = ((float)tx_power_1m - rssi) / (10.0f * path_loss_exponent);
    return powf(10.0f, exponent);
}

/* Безпечне зчитування Big-Endian 16-bit */
static inline uint16_t read_be16(const uint8_t *p) {
    return (uint16_t)((p[0] << 8) | p[1]);
}

/* Безпечне зчитування Big-Endian 32-bit */
static inline uint32_t read_be32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8)  | (uint32_t)p[3];
}

/* Декодування Eddystone-URL токенів */
static void decode_eddystone_url(const uint8_t *payload, uint8_t len, char *out, size_t out_max) {
    if (len < 1) return;
    out[0] = '\0';

    static const char *prefixes[] = {
        "http://www.", "https://www.", "http://", "https://"
    };
    uint8_t scheme = payload[0];
    if (scheme < 4) {
        snprintf(out, out_max, "%s", prefixes[scheme]);
    }

    static const char *suffixes[] = {
        ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",
        ".com",  ".org",  ".edu",  ".net",  ".info",  ".biz",  ".gov"
    };

    size_t cur_len = strlen(out);
    for (uint8_t i = 1; i < len; ++i) {
        uint8_t b = payload[i];
        if (b <= 0x0D) {
            strncat(out, suffixes[b], out_max - cur_len - 1);
            cur_len = strlen(out);
        } else if (b >= 32 && b <= 126) {
            if (cur_len + 1 < out_max) {
                out[cur_len++] = (char)b;
                out[cur_len] = '\0';
            }
        }
    }
}

/* Парсер буфера рекламних даних (31 байт) */
bool parse_ble_advertisement(const uint8_t *buf, size_t buf_len, parsed_beacon_t *out) {
    if (!buf || buf_len == 0 || !out) return false;
    memset(out, 0, sizeof(*out));

    size_t offset = 0;
    while (offset < buf_len) {
        uint8_t ad_len = buf[offset];
        if (ad_len == 0 || offset + 1 + ad_len > buf_len) break;

        uint8_t ad_type = buf[offset + 1];
        const uint8_t *ad_data = &buf[offset + 2];
        uint8_t data_len = ad_len - 1;

        /* Перевірка на Manufacturer Specific Data (0xFF) */
        if (ad_type == 0xFF && data_len >= 25) {
            uint16_t company = (uint16_t)(ad_data[0] | (ad_data[1] << 8));
            
            /* Apple iBeacon: Company ID = 0x004C, Type = 0x02, Subtype Len = 0x15 */
            if (company == 0x004C && ad_data[2] == 0x02 && ad_data[3] == 0x15) {
                const ibeacon_frame_t *ib = (const ibeacon_frame_t *)&buf[offset];
                out->type = BEACON_TYPE_IBEACON;
                memcpy(out->data.ibeacon.uuid, ib->uuid, 16);
                out->data.ibeacon.major = read_be16((const uint8_t *)&ib->major);
                out->data.ibeacon.minor = read_be16((const uint8_t *)&ib->minor);
                out->calibrated_power_1m = ib->measured_power;
                return true;
            }

            /* AltBeacon: Beacon Code = 0xBEAC */
            if (data_len >= 26 && ad_data[2] == 0xBE && ad_data[3] == 0xAC) {
                const altbeacon_frame_t *ab = (const altbeacon_frame_t *)&buf[offset];
                out->type = BEACON_TYPE_ALTBEACON;
                out->data.altbeacon.manufacturer_id = company;
                memcpy(out->data.altbeacon.beacon_id, ab->beacon_id, 20);
                out->calibrated_power_1m = ab->ref_rssi;
                return true;
            }
        }

        /* Перевірка на Service Data (0x16) для Google Eddystone (0xFEAA) */
        if (ad_type == 0x16 && data_len >= 3) {
            uint16_t service_uuid = (uint16_t)(ad_data[0] | (ad_data[1] << 8));
            if (service_uuid == 0xFEAA) {
                uint8_t frame_type = ad_data[2];
                if (frame_type == 0x00 && data_len >= 18) { /* UID */
                    const eddystone_uid_t *uid = (const eddystone_uid_t *)&ad_data[2];
                    out->type = BEACON_TYPE_EDDYSTONE_UID;
                    out->calibrated_power_1m = (int8_t)(uid->tx_power_0m - 41);
                    memcpy(out->data.eddystone_uid.namespace_id, uid->namespace_id, 10);
                    memcpy(out->data.eddystone_uid.instance_id, uid->instance_id, 6);
                    return true;
                } else if (frame_type == 0x10 && data_len >= 4) { /* URL */
                    out->type = BEACON_TYPE_EDDYSTONE_URL;
                    out->calibrated_power_1m = (int8_t)((int8_t)ad_data[3] - 41);
                    decode_eddystone_url(&ad_data[4], data_len - 4, out->data.eddystone_url.url, sizeof(out->data.eddystone_url.url));
                    return true;
                } else if (frame_type == 0x20 && data_len >= 14) { /* TLM */
                    const eddystone_tlm_t *tlm = (const eddystone_tlm_t *)&ad_data[2];
                    out->type = BEACON_TYPE_EDDYSTONE_TLM;
                    out->calibrated_power_1m = -59;
                    out->data.eddystone_tlm.battery_mv = read_be16((const uint8_t *)&tlm->vbatt_mv);
                    out->data.eddystone_tlm.temperature_c = (float)((int16_t)read_be16((const uint8_t *)&tlm->temp_fixed)) / 256.0f;
                    out->data.eddystone_tlm.adv_count = read_be32((const uint8_t *)&tlm->adv_cnt);
                    out->data.eddystone_tlm.uptime_sec = read_be32((const uint8_t *)&tlm->uptime_ticks) / 10;
                    return true;
                }
            }
        }

        offset += 1 + ad_len;
    }

    return false;
}

int main(void) {
    /* Тестовий пакет Apple iBeacon у сирому форматі BLE Advertising */
    const uint8_t raw_ibeacon[] = {
        0x02, 0x01, 0x06,                               /* Flags */
        0x1A, 0xFF, 0x4C, 0x00, 0x02, 0x15,             /* Header: Apple (0x004C), iBeacon */
        0xE2, 0xC5, 0x6D, 0xB5, 0xDF, 0xFB, 0x48, 0xD2, /* Proximity UUID (16B) */
        0xB0, 0x60, 0xD0, 0xF5, 0xA7, 0x10, 0x96, 0xE0,
        0x00, 0x0A,                                     /* Major = 10 */
        0x00, 0x02,                                     /* Minor = 2 */
        0xC5                                            /* TxPower @ 1m = -59 dBm */
    };

    parsed_beacon_t beacon;
    if (parse_ble_advertisement(raw_ibeacon, sizeof(raw_ibeacon), &beacon)) {
        printf("Знайдено iBeacon!\n");
        printf("Major: %u, Minor: %u, Calibrated TxPower@1m: %d dBm\n",
               beacon.data.ibeacon.major, beacon.data.ibeacon.minor, beacon.calibrated_power_1m);
    }

    /* Симуляція потоку зашумлених вимірювань RSSI та робота фільтра Калмана */
    kalman_filter_t kf;
    kalman_init(&kf, 0.05f, 4.0f);

    float raw_rssi_series[] = {-68.0f, -72.0f, -69.0f, -85.0f, -70.0f, -71.0f};
    printf("\nФільтрація шумів RSSI та оцінка відстані (n = 2.0):\n");
    for (size_t i = 0; i < sizeof(raw_rssi_series)/sizeof(raw_rssi_series[0]); ++i) {
        float raw = raw_rssi_series[i];
        float filtered = kalman_update(&kf, raw);
        float dist_raw = calculate_distance(beacon.calibrated_power_1m, raw, 2.0f);
        float dist_filtered = calculate_distance(beacon.calibrated_power_1m, filtered, 2.0f);
        printf("[%zu] Сирий: %5.1f dBm (d=%5.2f м) -> Калман: %5.1f dBm (d=%5.2f м)\n",
               i + 1, raw, dist_raw, filtered, dist_filtered);
    }

    return 0;
}
