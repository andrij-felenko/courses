#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <chrono>
#include <thread>
#include <mavlink.h>

namespace trajectory {

struct KinematicState {
    float x{0.0f}, y{0.0f}, z{0.0f};
    float vx{0.0f}, vy{0.0f}, vz{0.0f};
    float yaw{0.0f};
};

class CircularTrajectoryGenerator {
public:
    CircularTrajectoryGenerator(float radius_m, float angular_velocity_rad_s, float altitude_m) noexcept
        : radius_{radius_m}, omega_{angular_velocity_rad_s}, alt_{altitude_m} {}

    [[nodiscard]] KinematicState evaluate(float time_sec) const noexcept {
        KinematicState state{};
        const float angle = omega_ * time_sec;

        state.x = radius_ * std::cos(angle);
        state.y = radius_ * std::sin(angle);
        state.z = -alt_; // NED: висота від'ємна

        state.vx = -radius_ * omega_ * std::sin(angle);
        state.vy =  radius_ * omega_ * std::cos(angle);
        state.vz = 0.0f;

        // Ніс апарата дивиться за вектором поточної швидкості
        state.yaw = std::atan2(state.vy, state.vx);
        return state;
    }

private:
    float radius_{3.0f};
    float omega_{0.5f};
    float alt_{2.5f};
};

class OffboardStreamer {
public:
    explicit OffboardStreamer(uint8_t sys_id = 255, uint8_t comp_id = MAV_COMP_ID_ONBOARD_COMPUTER) noexcept
        : sys_id_{sys_id}, comp_id_{comp_id} {}

    [[nodiscard]] std::span<const uint8_t> pack_setpoint(
        const KinematicState& state,
        std::span<uint8_t> output_buffer) const noexcept
    {
        if (output_buffer.size() < MAVLINK_MAX_PACKET_LEN) {
            return {};
        }

        mavlink_set_position_target_local_ned_t sp{};
        sp.time_boot_ms = 0;
        sp.target_system = 1;
        sp.target_component = MAV_COMP_ID_AUTOPILOT1;
        sp.coordinate_frame = MAV_FRAME_LOCAL_NED;

        // Позиція + Швидкість + Курс активні (0x0DC0)
        sp.type_mask = POSITION_TARGET_TYPEMASK_AX_IGNORE |
                       POSITION_TARGET_TYPEMASK_AY_IGNORE |
                       POSITION_TARGET_TYPEMASK_AZ_IGNORE |
                       POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE;

        sp.x = state.x;
        sp.y = state.y;
        sp.z = state.z;
        sp.vx = state.vx;
        sp.vy = state.vy;
        sp.vz = state.vz;
        sp.yaw = state.yaw;

        mavlink_message_t msg{};
        mavlink_msg_set_position_target_local_ned_encode(sys_id_, comp_id_, &msg, &sp);

        const uint16_t len = mavlink_msg_to_send_buffer(output_buffer.data(), &msg);
        return output_buffer.subspan(0, len);
    }

private:
    uint8_t sys_id_{255};
    uint8_t comp_id_{MAV_COMP_ID_ONBOARD_COMPUTER};
};

} // namespace trajectory
