#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <unistd.h>
#include <mavlink.h>

// Перевірка числових параметрів уставки на коректність
bool validate_setpoint(float x, float y, float z, float vx, float vy, float vz, float yaw) {
    if (isnan(x) || isnan(y) || isnan(z) || isnan(vx) || isnan(vy) || isnan(vz) || isnan(yaw)) {
        return false;
    }
    if (isinf(x) || isinf(y) || isinf(z) || isinf(vx) || isinf(vy) || isinf(vz) || isinf(yaw)) {
        return false;
    }
    // Ліміт швидкості для безпеки (наприклад, не більше 15 м/с)
    float speed_sq = vx * vx + vy * vy + vz * vz;
    if (speed_sq > 225.0f) {
        return false;
    }
    return true;
}

// Формування кадру SET_POSITION_TARGET_LOCAL_NED з прямим зв'язком швидкості
int send_offboard_position_target(int serial_fd, uint8_t sys_id, uint8_t comp_id,
                                  float x, float y, float z,
                                  float vx, float vy, float vz,
                                  float yaw_rad) {
    if (!validate_setpoint(x, y, z, vx, vy, vz, yaw_rad)) {
        return -1;
    }

    mavlink_set_position_target_local_ned_t setpoint;
    memset(&setpoint, 0, sizeof(setpoint));

    // 0 = автопілот використовує власний поточний час прийому пакета
    setpoint.time_boot_ms = 0;
    setpoint.target_system = 1;
    setpoint.target_component = MAV_COMP_ID_AUTOPILOT1;
    setpoint.coordinate_frame = MAV_FRAME_LOCAL_NED;

    // Маска: Pos + Vel + Yaw активні, прискорення та yaw_rate ігноруються (0x0DC0)
    setpoint.type_mask = POSITION_TARGET_TYPEMASK_AX_IGNORE |
                         POSITION_TARGET_TYPEMASK_AY_IGNORE |
                         POSITION_TARGET_TYPEMASK_AZ_IGNORE |
                         POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE;

    // У системі NED вісь Z спрямована вниз, тому висота +5м задається як z = -5.0f
    setpoint.x = x;
    setpoint.y = y;
    setpoint.z = z;
    setpoint.vx = vx;
    setpoint.vy = vy;
    setpoint.vz = vz;
    setpoint.yaw = yaw_rad;

    mavlink_message_t msg;
    mavlink_msg_set_position_target_local_ned_encode(sys_id, comp_id, &msg, &setpoint);

    uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buffer, &msg);

    ssize_t written = write(serial_fd, buffer, len);
    return (written == (ssize_t)len) ? 0 : -1;
}

// Розрахунок Евклідової помилки слідування за позицією
float compute_tracking_error(float target_x, float target_y, float target_z,
                             const mavlink_local_position_ned_t *actual_pos) {
    float dx = target_x - actual_pos->x;
    float dy = target_y - actual_pos->y;
    float dz = target_z - actual_pos->z;
    return sqrtf(dx * dx + dy * dy + dz * dz);
}
