#include <mavlink.h>
#include <iostream>
#include <vector>
#include <cmath>
#include <array>

class HighLatencyTelemetryProvider {
public:
    static std::vector<uint8_t> buildPacket(uint8_t sys_id, uint8_t comp_id) {
        mavlink_message_t msg{};
        mavlink_high_latency2_t hl{};

        hl.timestamp = 3600000;
        hl.type = MAV_TYPE_FIXED_WING;
        hl.autopilot = MAV_AUTOPILOT_PX4;
        hl.custom_mode = 3;

        hl.latitude = static_cast<int32_t>(std::round(46.482526 * 1e7));
        hl.longitude = static_cast<int32_t>(std::round(30.723309 * 1e7));

        hl.altitude = 450;
        hl.target_altitude = 500;
        hl.heading = static_cast<uint8_t>(std::round(124.0 / 2.0));
        hl.target_heading = static_cast<uint8_t>(std::round(130.0 / 2.0));
        hl.target_distance = static_cast<uint16_t>(std::round(2450.0 / 10.0));
        hl.wp_num = 14;

        hl.throttle = 65;
        hl.airspeed = static_cast<uint8_t>(std::round(22.4 * 5.0));
        hl.airspeed_sp = static_cast<uint8_t>(std::round(22.0 * 5.0));
        hl.groundspeed = static_cast<uint8_t>(std::round(24.8 * 5.0));
        hl.climb_rate = static_cast<int8_t>(std::round(1.2 * 10.0));

        hl.battery = 78;
        hl.current_battery = static_cast<int16_t>(std::round(18.5 * 10.0));
        hl.temperature = 42;
        hl.temperature_air = 14;
        hl.failure_flags = 0;
        hl.failsafe = 0;

        mavlink_msg_high_latency2_encode(sys_id, comp_id, &msg, &hl);

        std::vector<uint8_t> buffer(MAVLINK_MAX_PACKET_LEN);
        const uint16_t len = mavlink_msg_to_send_buffer(buffer.data(), &msg);
        buffer.resize(len);

        return buffer;
    }
};
