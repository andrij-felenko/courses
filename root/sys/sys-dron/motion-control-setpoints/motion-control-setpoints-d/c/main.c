#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <unistd.h>
#include <mavlink.h>

// Розрахунок точки кругової траєкторії з прямим зв'язком за швидкістю
void compute_circular_trajectory(float t_sec, float radius, float omega,
                                 float *x, float *y, float *vx, float *vy) {
    // Положення на колі
    *x = radius * cosf(omega * t_sec);
    *y = radius * sinf(omega * t_sec);

    // Аналітична похідна положення (вектор швидкості)
    *vx = -radius * omega * sinf(omega * t_sec);
    *vy =  radius * omega * cosf(omega * t_sec);
}

// Функція циклічної відправки уставки в порт UART
bool stream_offboard_step(int serial_fd, float t_sec, float target_alt_m) {
    float x = 0.0f, y = 0.0f, vx = 0.0f, vy = 0.0f;
    compute_circular_trajectory(t_sec, 3.0f, 0.5f, &x, &y, &vx, &vy);

    mavlink_set_position_target_local_ned_t sp;
    memset(&sp, 0, sizeof(sp));

    sp.time_boot_ms = 0;
    sp.target_system = 1;
    sp.target_component = MAV_COMP_ID_AUTOPILOT1;
    sp.coordinate_frame = MAV_FRAME_LOCAL_NED;

    // Активні: X, Y, Z, Vx, Vy, Vz, Yaw. Прискорення та yaw_rate ігноруються (0x0DC0)
    sp.type_mask = POSITION_TARGET_TYPEMASK_AX_IGNORE |
                   POSITION_TARGET_TYPEMASK_AY_IGNORE |
                   POSITION_TARGET_TYPEMASK_AZ_IGNORE |
                   POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE;

    sp.x = x;
    sp.y = y;
    sp.z = -target_alt_m; // У системі NED висота є від'ємною координатою Z
    sp.vx = vx;
    sp.vy = vy;
    sp.vz = 0.0f;
    sp.yaw = atan2f(vy, vx); // Орієнтація носа дрона за вектором швидкості

    mavlink_message_t msg;
    mavlink_msg_set_position_target_local_ned_encode(255, MAV_COMP_ID_ONBOARD_COMPUTER, &msg, &sp);

    uint8_t tx_buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(tx_buf, &msg);

    ssize_t written = write(serial_fd, tx_buf, len);
    return (written == (ssize_t)len);
}
