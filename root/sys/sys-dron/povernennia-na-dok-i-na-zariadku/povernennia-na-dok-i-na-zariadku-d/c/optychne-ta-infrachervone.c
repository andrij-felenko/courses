mavlink_message_t msg;
mavlink_msg_landing_target_pack(
    system_id, companion_comp_id, &msg,
    time_boot_us,
    target_num,
    MAV_FRAME_BODY_NED,
    angle_x_rad, angle_y_rad,
    distance_m,
    size_x_rad, size_y_rad,
    pos_x_m, pos_y_m, pos_z_m,
    q_target_orientation,
    LANDING_TARGET_TYPE_VISION_FIDUCIAL,
    position_valid_flag
);
