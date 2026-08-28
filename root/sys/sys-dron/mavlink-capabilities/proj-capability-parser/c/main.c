#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#define MAV_CMD_REQUEST_MESSAGE 512
#define MSG_ID_AUTOPILOT_VERSION 148

#define CAP_MISSION_FLOAT  (1ULL << 0)
#define CAP_PARAM_FLOAT    (1ULL << 1)
#define CAP_MISSION_INT    (1ULL << 2)
#define CAP_COMMAND_INT    (1ULL << 3)
#define CAP_PARAM_UNION    (1ULL << 4)
#define CAP_FTP            (1ULL << 5)
#define CAP_SET_ATT_TARGET (1ULL << 6)
#define CAP_SET_POS_NED    (1ULL << 7)
#define CAP_TERRAIN        (1ULL << 9)
#define CAP_COMPASS_CAL    (1ULL << 11)
#define CAP_MAVLINK2       (1ULL << 12)
#define CAP_FLIGHT_INFO    (1ULL << 15)

typedef enum {
    NEG_STATE_IDLE,
    NEG_STATE_REQUESTING,
    NEG_STATE_WAITING,
    NEG_STATE_NEGOTIATED,
    NEG_STATE_FALLBACK
} neg_state_t;

typedef struct {
    uint8_t major;
    uint8_t minor;
    uint8_t patch;
    uint8_t release_type;
    char    version_str[32];
    char    git_hash_str[17];
    char    uid2_str[48];
    bool    supports_mission_int;
    bool    supports_ftp;
    bool    supports_param_union;
    bool    supports_mavlink2;
    bool    supports_offboard_ned;
    bool    supports_terrain;
    bool    supports_flight_info;
} vehicle_caps_t;

typedef struct {
    neg_state_t    state;
    uint8_t        target_sysid;
    uint8_t        target_compid;
    uint32_t       last_request_time_ms;
    uint8_t        retry_count;
    vehicle_caps_t caps;
} capability_negotiator_t;

// Ініціалізація автомата
void neg_init(capability_negotiator_t* neg, uint8_t sysid, uint8_t compid) {
    neg->state = NEG_STATE_IDLE;
    neg->target_sysid = sysid;
    neg->target_compid = compid;
    neg->last_request_time_ms = 0;
    neg->retry_count = 0;
    memset(&neg->caps, 0, sizeof(vehicle_caps_t));
}

// Запуск процедури після отримання HEARTBEAT
void neg_start(capability_negotiator_t* neg, uint32_t now_ms) {
    neg->state = NEG_STATE_REQUESTING;
    neg->retry_count = 0;
    neg->last_request_time_ms = now_ms;
}

// Періодичний крок оновлення (тайм-аути та повторні спроби)
void neg_update(capability_negotiator_t* neg, uint32_t now_ms) {
    if (neg->state == NEG_STATE_REQUESTING) {
        // Симуляція відправки COMMAND_LONG (MAV_CMD_REQUEST_MESSAGE, param1=148)
        printf("[C-Negotiator] Надсилання MAV_CMD_REQUEST_MESSAGE(#512) для AUTOPILOT_VERSION (спроба %d)\n",
               neg->retry_count + 1);
        neg->last_request_time_ms = now_ms;
        neg->state = NEG_STATE_WAITING;
    } else if (neg->state == NEG_STATE_WAITING) {
        if (now_ms - neg->last_request_time_ms > 1000) { // 1 секунда тайм-аут
            neg->retry_count++;
            if (neg->retry_count >= 3) {
                printf("[C-Negotiator] Тайм-аут відповіді вичерпано. Перехід у FALLBACK_DEGRADED.\n");
                neg->state = NEG_STATE_FALLBACK;
                // Налаштування базової консервативної сумісності
                neg->caps.supports_mission_int = false;
                neg->caps.supports_ftp = false;
                neg->caps.supports_mavlink2 = false;
                neg->caps.supports_terrain = false;
                neg->caps.supports_flight_info = false;
            } else {
                neg->state = NEG_STATE_REQUESTING;
            }
        }
    }
}

// Обробка отриманого пакета AUTOPILOT_VERSION
void neg_handle_version_msg(capability_negotiator_t* neg,
                            uint64_t capabilities,
                            uint32_t flight_sw_version,
                            const uint8_t flight_custom_version[8],
                            const uint8_t uid2[18]) {
    if (neg->state != NEG_STATE_WAITING && neg->state != NEG_STATE_REQUESTING) {
        return;
    }

    vehicle_caps_t* c = &neg->caps;

    // 1. Розпакування SemVer
    c->major        = (uint8_t)((flight_sw_version >> 24) & 0xFF);
    c->minor        = (uint8_t)((flight_sw_version >> 16) & 0xFF);
    c->patch        = (uint8_t)((flight_sw_version >> 8)  & 0xFF);
    c->release_type = (uint8_t)(flight_sw_version & 0xFF);

    const char* type_suffix = "";
    if (c->release_type == 0)        type_suffix = "-dev";
    else if (c->release_type == 64)  type_suffix = "-alpha";
    else if (c->release_type == 128) type_suffix = "-beta";
    else if (c->release_type == 192) type_suffix = "-rc";

    snprintf(c->version_str, sizeof(c->version_str), "v%u.%u.%u%s",
             c->major, c->minor, c->patch, type_suffix);

    // 2. Форматування Git хешу
    for (int i = 0; i < 8; ++i) {
        snprintf(&c->git_hash_str[i * 2], 3, "%02x", flight_custom_version[i]);
    }

    // 3. Форматування UID2
    int offset = 0;
    for (int i = 0; i < 18 && offset < (int)sizeof(c->uid2_str) - 3; ++i) {
        offset += snprintf(&c->uid2_str[offset], sizeof(c->uid2_str) - offset,
                           (i == 0) ? "%02X" : "-%02X", uid2[i]);
    }

    // 4. Оцінка бітової маски
    c->supports_mission_int   = (capabilities & CAP_MISSION_INT) != 0;
    c->supports_ftp           = (capabilities & CAP_FTP) != 0;
    c->supports_param_union   = (capabilities & CAP_PARAM_UNION) != 0;
    c->supports_mavlink2      = (capabilities & CAP_MAVLINK2) != 0;
    c->supports_offboard_ned  = (capabilities & CAP_SET_POS_NED) != 0;
    c->supports_terrain       = (capabilities & CAP_TERRAIN) != 0;
    c->supports_flight_info   = (capabilities & CAP_FLIGHT_INFO) != 0;

    neg->state = NEG_STATE_NEGOTIATED;

    printf("[C-Negotiator] Узгодження успішне!\n");
    printf("  Прошивка: %s (Git SHA: %s)\n", c->version_str, c->git_hash_str);
    printf("  UID2: %s\n", c->uid2_str);
    printf("  Підтримка: MISSION_INT=%d, FTP=%d, MAVLink2=%d, Terrain=%d, FlightInfo=%d\n",
           c->supports_mission_int, c->supports_ftp,
           c->supports_mavlink2, c->supports_terrain, c->supports_flight_info);
}
