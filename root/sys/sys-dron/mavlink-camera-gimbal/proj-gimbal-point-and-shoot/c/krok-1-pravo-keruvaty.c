#define MY_SYS       1
#define MY_COMP      MAV_COMP_ID_ONBOARD_COMPUTER  /* 191 */
#define MANAGER_COMP MAV_COMP_ID_AUTOPILOT1        /* 1   */
#define DEVICE_COMP  MAV_COMP_ID_GIMBAL            /* 154 */
#define CAMERA_COMP  MAV_COMP_ID_CAMERA            /* 100 */

static void send_command(uint16_t cmd, uint8_t target_comp, const float p[7])
{
    mavlink_message_t m;
    mavlink_msg_command_long_pack(MY_SYS, MY_COMP, &m,
                                  MY_SYS, target_comp, cmd, /* confirmation */ 0,
                                  p[0], p[1], p[2], p[3], p[4], p[5], p[6]);
    send_msg(&m);
}

static void take_primary_control(void)
{
    const float p[7] = {
        (float)MY_SYS, (float)MY_COMP,  /* первинний розпорядник — це я */
        -1.0f, -1.0f,                   /* вторинного не чіпаємо        */
        0.0f, 0.0f, (float)DEVICE_COMP  /* param7 — котрий саме пристрій */
    };
    send_command(MAV_CMD_DO_GIMBAL_MANAGER_CONFIGURE, MANAGER_COMP, p);
}
