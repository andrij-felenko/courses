bool point_and_shoot(const geo_t *target, int32_t *image_index)
{
    take_primary_control();

    if (!pose_fresh(200)) return false;     /* поза старша за 200 мс — не наводимо */

    float pitch, yaw_earth;
    aim_angles(&g_pose, target, &yaw_earth, &pitch);

    if (!point_gimbal(&g_dev_info, pitch, yaw_earth, g_vehicle_yaw)) return false;

    const uint32_t caps = g_dev_info.cap_flags2 ? g_dev_info.cap_flags2
                                                : g_dev_info.cap_flags;
    const bool earth = caps & GIMBAL_DEVICE_CAP_FLAGS_SUPPORTS_YAW_IN_EARTH_FRAME;
    const float want_yaw = earth ? yaw_earth
                                 : wrap_pi(yaw_earth - g_vehicle_yaw);

    if (!wait_on_target(pitch, want_yaw, earth, 0.017f /* ≈1° */, 4000)) return false;

    return shoot_one(image_index, 5000);
}
