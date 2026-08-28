#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <optional>
#include <mavlink.h>

namespace drone_control {

enum class Frame : uint8_t {
    LocalNed       = MAV_FRAME_LOCAL_NED,
    LocalOffsetNed = MAV_FRAME_LOCAL_OFFSET_NED,
    BodyNed        = MAV_FRAME_BODY_NED,
    BodyOffsetNed  = MAV_FRAME_BODY_OFFSET_NED,
    BodyFrd        = MAV_FRAME_BODY_FRD
};

struct SetpointCommand {
    float x{0.0f}, y{0.0f}, z{0.0f};
    float vx{0.0f}, vy{0.0f}, vz{0.0f};
    float afx{0.0f}, afy{0.0f}, afz{0.0f};
    float yaw{0.0f};
    float yaw_rate{0.0f};
    uint16_t type_mask{0x0DC0}; // За замовчуванням Pos + Vel + Yaw активні
    Frame frame{Frame::LocalNed};

    [[nodiscard]] bool is_valid() const noexcept {
        if (std::isnan(x) || std::isnan(y) || std::isnan(z) ||
            std::isnan(vx) || std::isnan(vy) || std::isnan(vz) ||
            std::isnan(yaw)) {
            return false;
        }
        if (std::isinf(x) || std::isinf(y) || std::isinf(z) ||
            std::isinf(vx) || std::isinf(vy) || std::isinf(vz) ||
            std::isinf(yaw)) {
            return false;
        }
        const float speed_sq = vx * vx + vy * vy + vz * vz;
        return speed_sq <= 400.0f; // Максимум 20 м/с
    }
};

class SetpointEncoder {
public:
    explicit SetpointEncoder(uint8_t source_sys = 255, uint8_t source_comp = MAV_COMP_ID_ONBOARD_COMPUTER) noexcept
        : sys_id_{source_sys}, comp_id_{source_comp} {}

    // Серіалізує уставку в наданий буфер span; повертає зріз записаних байтів
    [[nodiscard]] std::span<const uint8_t> encode(
        const SetpointCommand& cmd,
        std::span<uint8_t> output_buffer,
        uint8_t target_sys = 1,
        uint8_t target_comp = MAV_COMP_ID_AUTOPILOT1) const noexcept
    {
        if (!cmd.is_valid() || output_buffer.size() < MAVLINK_MAX_PACKET_LEN) {
            return {};
        }

        mavlink_set_position_target_local_ned_t raw{};
        raw.time_boot_ms = 0;
        raw.target_system = target_sys;
        raw.target_component = target_comp;
        raw.coordinate_frame = static_cast<uint8_t>(cmd.frame);
        raw.type_mask = cmd.type_mask;

        raw.x = cmd.x;
        raw.y = cmd.y;
        raw.z = cmd.z;
        raw.vx = cmd.vx;
        raw.vy = cmd.vy;
        raw.vz = cmd.vz;
        raw.afx = cmd.afx;
        raw.afy = cmd.afy;
        raw.afz = cmd.afz;
        raw.yaw = cmd.yaw;
        raw.yaw_rate = cmd.yaw_rate;

        mavlink_message_t msg{};
        mavlink_msg_set_position_target_local_ned_encode(sys_id_, comp_id_, &msg, &raw);

        const uint16_t written = mavlink_msg_to_send_buffer(output_buffer.data(), &msg);
        return output_buffer.subspan(0, written);
    }

    // Оцінка Евклідової помилки між цільовою уставкою та фактичною телеметрією
    [[nodiscard]] static float compute_error(
        const SetpointCommand& target,
        const mavlink_local_position_ned_t& telemetry) noexcept
    {
        const float dx = target.x - telemetry.x;
        const float dy = target.y - telemetry.y;
        const float dz = target.z - telemetry.z;
        return std::sqrt(dx * dx + dy * dy + dz * dz);
    }

private:
    uint8_t sys_id_{255};
    uint8_t comp_id_{MAV_COMP_ID_ONBOARD_COMPUTER};
};

} // namespace drone_control
