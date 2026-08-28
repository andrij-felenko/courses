#include <stdint.h>
#include <string.h>
#include <common/mavlink.h>

void pack_velocity_setpoint(mavlink_message_t *msg,
                            uint8_t sys_id, uint8_t comp_id,
                            float vx_ms, float vy_ms, float vz_ms,
                            float yaw_rad)
{
    mavlink_set_position_target_local_ned_t sp;
    memset(&sp, 0, sizeof(sp));

    sp.time_boot_ms = 0;
    sp.target_system = 1;
    sp.target_component = MAV_COMP_ID_AUTOPILOT1;
    sp.coordinate_frame = MAV_FRAME_LOCAL_NED;

    /* Маска: ігноруємо позицію, прискорення та швидкість yaw */
    sp.type_mask = MAVLINK_MSG_SET_POSITION_TARGET_LOCAL_NED_POSITION_TRAINED_IGNORE
                 | 0x0001 | 0x0002 | 0x0004   /* ignore X, Y, Z */
                 | 0x0040 | 0x0080 | 0x0100   /* ignore AFX, AFY, AFZ */
                 | 0x0800;                    /* ignore yaw_rate */

    sp.vx = vx_ms;
    sp.vy = vy_ms;
    sp.vz = vz_ms;
    sp.yaw = yaw_rad;

    mavlink_msg_set_position_target_local_ned_encode(sys_id, comp_id, msg, &sp);
}
