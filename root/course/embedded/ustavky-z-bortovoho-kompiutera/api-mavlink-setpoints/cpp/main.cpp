#include <cstdint>
#include <cstring>
#include <span>
#include <common/mavlink.h>

struct VelocitySetpoint {
    float vx_ms{0.0f};
    float vy_ms{0.0f};
    float vz_ms{0.0f};
    float yaw_rad{0.0f};
};

[[nodiscard]] mavlink_message_t encode_velocity_target(uint8_t sys_id,
                                                       uint8_t comp_id,
                                                       const VelocitySetpoint& target) noexcept
{
    mavlink_set_position_target_local_ned_t sp{};
    sp.time_boot_ms = 0;
    sp.target_system = 1;
    sp.target_component = MAV_COMP_ID_AUTOPILOT1;
    sp.coordinate_frame = MAV_FRAME_LOCAL_NED;

    /* Бітова маска: ігноруємо X, Y, Z, прискорення та yaw_rate */
    constexpr uint16_t mask = 0x0001 | 0x0002 | 0x0004   // Ignore Position
                            | 0x0040 | 0x0080 | 0x0100   // Ignore Accel
                            | 0x0800;                    // Ignore Yaw Rate
    sp.type_mask = mask;

    sp.vx = target.vx_ms;
    sp.vy = target.vy_ms;
    sp.vz = target.vz_ms;
    sp.yaw = target.yaw_rad;

    mavlink_message_t msg{};
    mavlink_msg_set_position_target_local_ned_encode(sys_id, comp_id, &msg, &sp);
    return msg;
}
