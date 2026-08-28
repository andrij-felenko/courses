#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

#define CAP_MISSION_INT  (1ULL << 2)
#define CAP_PARAM_UNION  (1ULL << 4)
#define CAP_FTP          (1ULL << 5)
#define CAP_MAVLINK2     (1ULL << 12)

typedef struct {
    uint8_t major;
    uint8_t minor;
    uint8_t patch;
    uint8_t release_type;
    char    version_str[32];
    bool    use_int_waypoints;
    bool    use_ftp_params;
    bool    use_mavlink2;
} parsed_autopilot_info_t;

// Декодування сирих полів AUTOPILOT_VERSION
void parse_autopilot_version(uint64_t capabilities,
                             uint32_t flight_sw_version,
                             parsed_autopilot_info_t* out_info) {
    // 1. Розпакування SemVer
    out_info->major        = (uint8_t)((flight_sw_version >> 24) & 0xFF);
    out_info->minor        = (uint8_t)((flight_sw_version >> 16) & 0xFF);
    out_info->patch        = (uint8_t)((flight_sw_version >> 8)  & 0xFF);
    out_info->release_type = (uint8_t)(flight_sw_version & 0xFF);

    const char* suffix = "";
    if (out_info->release_type == 0)        suffix = "-dev";
    else if (out_info->release_type == 64)  suffix = "-alpha";
    else if (out_info->release_type == 128) suffix = "-beta";
    else if (out_info->release_type == 192) suffix = "-rc";

    snprintf(out_info->version_str, sizeof(out_info->version_str),
             "v%u.%u.%u%s", out_info->major, out_info->minor,
             out_info->patch, suffix);

    // 2. Аналіз маски capabilities
    out_info->use_int_waypoints = (capabilities & CAP_MISSION_INT) != 0;
    out_info->use_ftp_params    = (capabilities & CAP_FTP) != 0;
    out_info->use_mavlink2       = (capabilities & CAP_MAVLINK2) != 0;
}
