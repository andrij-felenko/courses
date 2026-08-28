#pragma once

#include <cstdint>
#include <array>
#include <optional>
#include <span>
#include <cmath>
#include <algorithm>

namespace mavlink {

struct HighLatency2 {
    uint32_t timestamp_ms{0};
    double   latitude_deg{0.0};
    double   longitude_deg{0.0};
    uint16_t custom_mode{0};
    int16_t  altitude_m{0};
    int16_t  target_altitude_m{0};
    float    target_distance_m{0.0f};
    uint16_t waypoint_index{0};
    HlFailureFlag failure_flags{static_cast<HlFailureFlag>(0)};
    float    battery_current_a{0.0f};
    uint8_t  system_type{0};
    uint8_t  autopilot_type{0};
    float    heading_deg{0.0f};
    float    target_heading_deg{0.0f};
    uint8_t  throttle_pct{0};
    float    airspeed_mps{0.0f};
    float    airspeed_sp_mps{0.0f};
    float    groundspeed_mps{0.0f};
    float    windspeed_mps{0.0f};
    float    wind_heading_deg{0.0f};
    float    eph_m{0.0f};
    float    epv_m{0.0f};
    int8_t   air_temperature_c{0};
    float    climb_rate_mps{0.0f};
    int8_t   battery_pct{0};
    int8_t   custom0{0};
    int8_t   custom1{0};
    int8_t   custom2{0};
    int8_t   board_temperature_c{0};
    uint8_t  failsafe_flags{0};

    [[nodiscard]] std::array<uint8_t, 65> serialize() const noexcept {
        std::array<uint8_t, 65> buf{};
        auto write_u32 = [&](size_t off, uint32_t v) {
            buf[off] = static_cast<uint8_t>(v);
            buf[off+1] = static_cast<uint8_t>(v >> 8);
            buf[off+2] = static_cast<uint8_t>(v >> 16);
            buf[off+3] = static_cast<uint8_t>(v >> 24);
        };
        auto write_i32 = [&](size_t off, int32_t v) { write_u32(off, static_cast<uint32_t>(v)); };
        auto write_u16 = [&](size_t off, uint16_t v) {
            buf[off] = static_cast<uint8_t>(v);
            buf[off+1] = static_cast<uint8_t>(v >> 8);
        };
        auto write_i16 = [&](size_t off, int16_t v) { write_u16(off, static_cast<uint16_t>(v)); };

        write_u32(0, timestamp_ms);
        write_i32(4, static_cast<int32_t>(std::round(latitude_deg * 1e7)));
        write_i32(8, static_cast<int32_t>(std::round(longitude_deg * 1e7)));
        write_u16(12, custom_mode);
        write_i16(14, altitude_m);
        write_i16(16, target_altitude_m);
        write_u16(18, static_cast<uint16_t>(std::clamp(std::round(target_distance_m / 10.0f), 0.0f, 65535.0f)));
        write_u16(20, waypoint_index);
        write_u16(22, static_cast<uint16_t>(failure_flags));
        write_i16(24, static_cast<int16_t>(std::round(battery_current_a * 10.0f)));

        buf[26] = system_type;
        buf[27] = autopilot_type;
        buf[28] = static_cast<uint8_t>(std::fmod(std::round(heading_deg / 2.0f), 180.0f));
        buf[29] = static_cast<uint8_t>(std::fmod(std::round(target_heading_deg / 2.0f), 180.0f));
        buf[30] = throttle_pct;
        buf[31] = static_cast<uint8_t>(std::clamp(std::round(airspeed_mps * 5.0f), 0.0f, 255.0f));
        buf[32] = static_cast<uint8_t>(std::clamp(std::round(airspeed_sp_mps * 5.0f), 0.0f, 255.0f));
        buf[33] = static_cast<uint8_t>(std::clamp(std::round(groundspeed_mps * 5.0f), 0.0f, 255.0f));
        buf[34] = static_cast<uint8_t>(std::clamp(std::round(windspeed_mps * 5.0f), 0.0f, 255.0f));
        buf[35] = static_cast<uint8_t>(std::fmod(std::round(wind_heading_deg / 2.0f), 180.0f));
        buf[36] = static_cast<uint8_t>(std::clamp(std::round(eph_m * 10.0f), 0.0f, 255.0f));
        buf[37] = static_cast<uint8_t>(std::clamp(std::round(epv_m * 10.0f), 0.0f, 255.0f));
        buf[38] = static_cast<uint8_t>(air_temperature_c);
        buf[39] = static_cast<uint8_t>(static_cast<int8_t>(std::clamp(std::round(climb_rate_mps * 10.0f), -128.0f, 127.0f)));
        buf[40] = static_cast<uint8_t>(battery_pct);
        buf[41] = static_cast<uint8_t>(custom0);
        buf[42] = static_cast<uint8_t>(custom1);
        buf[43] = static_cast<uint8_t>(custom2);
        buf[44] = static_cast<uint8_t>(board_temperature_c);
        buf[45] = failsafe_flags;

        return buf;
    }

    static HighLatency2 deserialize(std::span<const uint8_t, 65> data) noexcept {
        HighLatency2 msg{};
        auto read_u32 = [&](size_t off) -> uint32_t {
            return static_cast<uint32_t>(data[off]) |
                   (static_cast<uint32_t>(data[off+1]) << 8) |
                   (static_cast<uint32_t>(data[off+2]) << 16) |
                   (static_cast<uint32_t>(data[off+3]) << 24);
        };
        auto read_i32 = [&](size_t off) -> int32_t { return static_cast<int32_t>(read_u32(off)); };
        auto read_u16 = [&](size_t off) -> uint16_t {
            return static_cast<uint16_t>(data[off]) | (static_cast<uint16_t>(data[off+1]) << 8);
        };
        auto read_i16 = [&](size_t off) -> int16_t { return static_cast<int16_t>(read_u16(off)); };

        msg.timestamp_ms = read_u32(0);
        msg.latitude_deg = static_cast<double>(read_i32(4)) * 1e-7;
        msg.longitude_deg = static_cast<double>(read_i32(8)) * 1e-7;
        msg.custom_mode = read_u16(12);
        msg.altitude_m = read_i16(14);
        msg.target_altitude_m = read_i16(16);
        msg.target_distance_m = static_cast<float>(read_u16(18)) * 10.0f;
        msg.waypoint_index = read_u16(20);
        msg.failure_flags = static_cast<HlFailureFlag>(read_u16(22));
        msg.battery_current_a = static_cast<float>(read_i16(24)) * 0.1f;

        msg.system_type = data[26];
        msg.autopilot_type = data[27];
        msg.heading_deg = static_cast<float>(data[28]) * 2.0f;
        msg.target_heading_deg = static_cast<float>(data[29]) * 2.0f;
        msg.throttle_pct = data[30];
        msg.airspeed_mps = static_cast<float>(data[31]) / 5.0f;
        msg.airspeed_sp_mps = static_cast<float>(data[32]) / 5.0f;
        msg.groundspeed_mps = static_cast<float>(data[33]) / 5.0f;
        msg.windspeed_mps = static_cast<float>(data[34]) / 5.0f;
        msg.wind_heading_deg = static_cast<float>(data[35]) * 2.0f;
        msg.eph_m = static_cast<float>(data[36]) * 0.1f;
        msg.epv_m = static_cast<float>(data[37]) * 0.1f;
        msg.air_temperature_c = static_cast<int8_t>(data[38]);
        msg.climb_rate_mps = static_cast<float>(static_cast<int8_t>(data[39])) * 0.1f;
        msg.battery_pct = static_cast<int8_t>(data[40]);
        msg.custom0 = static_cast<int8_t>(data[41]);
        msg.custom1 = static_cast<int8_t>(data[42]);
        msg.custom2 = static_cast<int8_t>(data[43]);
        msg.board_temperature_c = static_cast<int8_t>(data[44]);
        msg.failsafe_flags = data[45];

        return msg;
    }
};

} // namespace mavlink
