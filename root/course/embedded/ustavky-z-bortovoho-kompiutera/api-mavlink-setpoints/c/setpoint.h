#ifndef SETPOINT_H
#define SETPOINT_H

#include <stdint.h>

#include <common/mavlink.h>

/* Біти type_mask повідомлення #84: одиниця = «поле не читати».
   Числа виписані явно навмисно: набір енумераторів у генерованих
   заголовках MAVLink різниться від збірки до збірки, а самі значення
   зафіксовані специфікацією кадру й не змінюються. */
enum {
    PT_IGN_X        = 0x0001,
    PT_IGN_Y        = 0x0002,
    PT_IGN_Z        = 0x0004,
    PT_IGN_VX       = 0x0008,
    PT_IGN_VY       = 0x0010,
    PT_IGN_VZ       = 0x0020,
    PT_IGN_AFX      = 0x0040,
    PT_IGN_AFY      = 0x0080,
    PT_IGN_AFZ      = 0x0100,
    PT_FORCE        = 0x0200,   /* біт не про ігнорування: 1 = afx/afy/afz у Ньютонах */
    PT_IGN_YAW      = 0x0400,
    PT_IGN_YAW_RATE = 0x0800
};

/* Робочі конфігурації масок. */
#define PT_MASK_POSITION \
    (PT_IGN_VX | PT_IGN_VY | PT_IGN_VZ | PT_IGN_AFX | PT_IGN_AFY | PT_IGN_AFZ | PT_IGN_YAW_RATE)   /* 0x0DF8 */
#define PT_MASK_VELOCITY \
    (PT_IGN_X | PT_IGN_Y | PT_IGN_Z | PT_IGN_AFX | PT_IGN_AFY | PT_IGN_AFZ | PT_IGN_YAW_RATE)      /* 0x0DC7 */
#define PT_MASK_VELOCITY_YAWRATE \
    (PT_IGN_X | PT_IGN_Y | PT_IGN_Z | PT_IGN_AFX | PT_IGN_AFY | PT_IGN_AFZ | PT_IGN_YAW)           /* 0x05C7 */
#define PT_MASK_POSITION_FF_VELOCITY \
    (PT_IGN_AFX | PT_IGN_AFY | PT_IGN_AFZ | PT_IGN_YAW_RATE)                                       /* 0x09C0 */

/* Біти type_mask повідомлення #83 (уже 8-бітового). */
enum {
    AT_IGN_ROLL_RATE  = 0x01,
    AT_IGN_PITCH_RATE = 0x02,
    AT_IGN_YAW_RATE   = 0x04,
    AT_IGN_THROTTLE   = 0x40,
    AT_IGN_ATTITUDE   = 0x80
};

#define AT_MASK_ATTITUDE_THRUST (AT_IGN_ROLL_RATE | AT_IGN_PITCH_RATE | AT_IGN_YAW_RATE)  /* 0x07 */
#define AT_MASK_RATES_THRUST    (AT_IGN_ATTITUDE)                                         /* 0x80 */

/* Усі будівники повертають 0 або -1, якщо в уставку потрапило нечисло
   (NaN/inf) чи вироджений кватерніон. Кадр із NaN автопілот приймає
   мовчки, а поводиться після нього непередбачувано — тому фільтруємо тут. */

int sp_position_ned(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                    uint32_t boot_ms, float north_m, float east_m, float down_m, float yaw_rad);

int sp_velocity_ned(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                    uint32_t boot_ms, float vn_ms, float ve_ms, float vd_ms, float yaw_rad);

int sp_velocity_yawrate(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                        uint32_t boot_ms, float vn_ms, float ve_ms, float vd_ms, float yaw_rate_rads);

int sp_position_ff_velocity(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                            uint32_t boot_ms,
                            float north_m, float east_m, float down_m,
                            float vn_ms, float ve_ms, float vd_ms, float yaw_rad);

int sp_attitude_thrust(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                       uint32_t boot_ms, const float q[4], float thrust);

int sp_body_rates(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                  uint32_t boot_ms, float roll_rate, float pitch_rate, float yaw_rate, float thrust);

/* Кватерніон [w x y z] із кутів Ейлера (послідовність Z-Y-X, як в ATTITUDE). */
void sp_quat_from_euler(float roll, float pitch, float yaw, float q_out[4]);

#endif /* SETPOINT_H */
