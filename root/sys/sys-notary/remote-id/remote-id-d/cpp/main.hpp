#include <cstdint>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <span>

namespace remote_id {

#pragma pack(push, 1)

struct alignas(1) LocationMessage {
    uint8_t  header{0x11};
    uint8_t  status_flags{0x20}; /* Airborne */
    uint8_t  direction{0};
    uint8_t  speed_h{0};
    int8_t   speed_v{0};
    int32_t  lat{0};
    int32_t  lon{0};
    uint16_t alt_geodetic{0};
    uint16_t alt_pressure{0};
    uint16_t height_agl{0};
    uint8_t  accuracy_horiz_vert{0xBA}; /* HAcc=11, VAcc=10 */
    uint8_t  accuracy_baro_speed{0xAA};
    uint16_t timestamp_tenths{0};
    uint8_t  time_adv_acc{0x10};
    uint8_t  reserved{0};

    LocationMessage(double latitude, double longitude, double alt_wgs84,
                    double speed_horiz, double speed_vert, double heading,
                    uint32_t sec_in_hour, uint32_t ms_part) noexcept {
        int deg = static_cast<int>(std::round(heading));
        direction = static_cast<uint8_t>((deg >= 0 ? deg : deg + 360) % 360);

        speed_h = static_cast<uint8_t>(std::clamp(speed_horiz / 0.25, 0.0, 254.0));
        speed_v = static_cast<int8_t>(std::clamp(speed_vert / 0.5, -127.0, 127.0));

        lat = static_cast<int32_t>(std::round(latitude * 1e7));
        lon = static_cast<int32_t>(std::round(longitude * 1e7));

        double enc_alt = std::clamp((alt_wgs84 + 1000.0) / 0.5, 0.0, 65535.0);
        alt_geodetic = static_cast<uint16_t>(std::round(enc_alt));
        alt_pressure = alt_geodetic;

        timestamp_tenths = static_cast<uint16_t>(((sec_in_hour % 3600) * 10 + (ms_part / 100)) % 36000);
    }

    [[nodiscard]] std::span<const uint8_t> bytes() const noexcept {
        return {reinterpret_cast<const uint8_t*>(this), sizeof(LocationMessage)};
    }
};

#pragma pack(pop)

} // namespace remote_id
