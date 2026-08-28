static bool point_gimbal(const mavlink_gimbal_device_information_t *info,
                         float pitch, float yaw_earth, float vehicle_yaw)
{
    const float yaw_body = wrap_pi(yaw_earth - vehicle_yaw);
    if (!within_limits(info, pitch, yaw_body))
        return false;                       /* просити неможливе — гірше, ніж не просити */

    const uint32_t caps = info->cap_flags2 ? info->cap_flags2 : info->cap_flags;
    const bool earth = caps & GIMBAL_DEVICE_CAP_FLAGS_SUPPORTS_YAW_IN_EARTH_FRAME;

    mavlink_message_t m;
    mavlink_msg_gimbal_manager_set_pitchyaw_pack(
        MY_SYS, MY_COMP, &m,
        MY_SYS, MANAGER_COMP,
        earth ? GIMBAL_MANAGER_FLAGS_YAW_IN_EARTH_FRAME
              : GIMBAL_MANAGER_FLAGS_YAW_IN_VEHICLE_FRAME,
        DEVICE_COMP,
        pitch,                              /* радіани, не градуси! */
        earth ? yaw_earth : yaw_body,
        NAN, NAN);                          /* швидкості не задаю — тримай як знаєш */
    send_msg(&m);
    return true;
}
