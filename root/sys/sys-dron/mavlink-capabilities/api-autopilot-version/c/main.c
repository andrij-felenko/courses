#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Бітова маска можливостей MAVLink
#define CAP_MISSION_FLOAT  (1ULL << 0)
#define CAP_PARAM_FLOAT    (1ULL << 1)
#define CAP_MISSION_INT    (1ULL << 2)
#define CAP_COMMAND_INT    (1ULL << 3)
#define CAP_PARAM_UNION    (1ULL << 4)
#define CAP_FTP            (1ULL << 5)
#define CAP_MAVLINK2       (1ULL << 12)

typedef struct {
    uint64_t capabilities;
    uint64_t uid;
    uint32_t flight_sw_version;
    uint32_t middleware_sw_version;
    uint32_t os_sw_version;
    uint32_t board_version;
    uint8_t  flight_custom_version[8];
    uint8_t  middleware_custom_version[8];
    uint8_t  os_custom_version[8];
    uint16_t vendor_id;
    uint16_t product_id;
    uint8_t  uid2[18];
} autopilot_version_payload_t;

// Перевірка готовності апарата до швидкісного обміну
bool is_high_speed_capable(const autopilot_version_payload_t* msg) {
    uint64_t mask = CAP_MISSION_INT | CAP_FTP | CAP_MAVLINK2;
    return (msg->capabilities & mask) == mask;
}

// Формування 32-бітного числа SemVer
uint32_t pack_semver(uint8_t major, uint8_t minor, uint8_t patch, uint8_t type) {
    return ((uint32_t)major << 24) |
           ((uint32_t)minor << 16) |
           ((uint32_t)patch << 8)  |
           ((uint32_t)type);
}
