#include <array>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <span>
#include <algorithm>
#include <string_view>

namespace remote_id {

inline constexpr std::size_t MsgSize = 25;
inline constexpr uint8_t ProtocolVersion = 0x01;
inline constexpr uint16_t OpenDroneIdUuid = 0xFFFA;

enum class MsgType : uint8_t {
    BasicId   = 0x0,
    Location  = 0x1,
    Auth      = 0x2,
    SelfId    = 0x3,
    System    = 0x4,
    Operator  = 0x5,
    Pack      = 0xF
};

enum class IdType : uint8_t {
    SerialNumber = 1,
    Caa          = 2,
    SessionId    = 4
};

enum class UaType : uint8_t {
    Aeroplane   = 1,
    Helicopter  = 2,
    Multirotor  = 15
};

enum class FlightStatus : uint8_t {
    Undeclared = 0,
    Ground     = 1,
    Airborne   = 2,
    Emergency  = 3
};

#pragma pack(push, 1)

struct alignas(1) BasicIdMessage {
    uint8_t header{static_cast<uint8_t>((static_cast<uint8_t>(MsgType::BasicId) << 4) | (ProtocolVersion & 0x0F))};
    uint8_t id_ua_type{0};
    std::array<uint8_t, 20> uas_id{};
    std::array<uint8_t, 3> reserved{};

    constexpr BasicIdMessage(IdType id_type, UaType ua_type, std::string_view serial) noexcept {
        id_ua_type = static_cast<uint8_t>((static_cast<uint8_t>(id_type) << 4) | (static_cast<uint8_t>(ua_type) & 0x0F));
        const auto copy_len = std::min(serial.size(), uas_id.size());
        for (std::size_t i = 0; i < copy_len; ++i) {
            uas_id[i] = static_cast<uint8_t>(serial[i]);
        }
    }
};

struct alignas(1) LocationMessage {
    uint8_t header{static_cast<uint8_t>((static_cast<uint8_t>(MsgType::Location) << 4) | (ProtocolVersion & 0x0F))};
    uint8_t status_flags{0};
    uint8_t direction{0};
    uint8_t speed_horizontal{0};
    int8_t  speed_vertical{0};
    int32_t latitude{0};
    int32_t longitude{0};
    uint16_t altitude_geodetic{0};
    uint16_t altitude_pressure{0};
    uint16_t height_agl{0};
    uint8_t horiz_vert_acc{0xBA}; /* HAcc=11, VAcc=10 */
    uint8_t baro_speed_acc{0xAA}; /* BaroAcc=10, SpeedAcc=10 */
    uint16_t timestamp{0};
    uint8_t time_adv_acc{0x10};
    uint8_t reserved{0};

    LocationMessage(FlightStatus status, double lat_deg, double lon_deg, double alt_m,
                    double speed_h, double speed_v, double heading_deg,
                    uint32_t sec_in_hour, uint32_t ms_part) noexcept {
        status_flags = static_cast<uint8_t>(static_cast<uint8_t>(status) << 4);

        int hdg = static_cast<int>(std::round(heading_deg));
        if (hdg < 0) hdg = (hdg % 360) + 360;
        direction = static_cast<uint8_t>(hdg % 360);

        speed_horizontal = static_cast<uint8_t>(std::clamp(speed_h / 0.25, 0.0, 254.0));
        speed_vertical = static_cast<int8_t>(std::clamp(speed_v / 0.5, -127.0, 127.0));

        latitude = static_cast<int32_t>(std::round(lat_deg * 1e7));
        longitude = static_cast<int32_t>(std::round(lon_deg * 1e7));

        double alt_enc = std::clamp((alt_m + 1000.0) / 0.5, 0.0, 65535.0);
        altitude_geodetic = static_cast<uint16_t>(std::round(alt_enc));
        altitude_pressure = altitude_geodetic;

        uint32_t tenths = (sec_in_hour % 3600) * 10 + (ms_part / 100);
        timestamp = static_cast<uint16_t>(tenths % 36000);
    }
};

struct alignas(1) Ble4Packet {
    uint8_t flags_len{0x02};
    uint8_t flags_type{0x01};
    uint8_t flags_val{0x06};

    uint8_t service_len{0x1B};
    uint8_t service_type{0x16};
    uint8_t uuid_lo{static_cast<uint8_t>(OpenDroneIdUuid & 0xFF)};
    uint8_t uuid_hi{static_cast<uint8_t>((OpenDroneIdUuid >> 8) & 0xFF)};
    std::array<uint8_t, MsgSize> payload{};

    template <typename TMsg>
    explicit Ble4Packet(const TMsg& msg) noexcept {
        static_assert(sizeof(TMsg) == MsgSize, "Повідомлення Open Drone ID повинно мати рівно 25 байтів");
        std::memcpy(payload.data(), &msg, MsgSize);
    }

    [[nodiscard]] std::span<const uint8_t> as_bytes() const noexcept {
        return {reinterpret_cast<const uint8_t*>(this), sizeof(Ble4Packet)};
    }
};

#pragma pack(pop)

} // namespace remote_id
