int run_msckf_example(void) {
    MsckfConfig cfg;
    /* Заповнення типових параметрів */
    cfg.body_T_cam = (MsckfVec3){0.1, 0.0, -0.05};
    cfg.body_R_cam = (MsckfQuat){1.0, 0.0, 0.0, 0.0};
    cfg.max_window_size = 15;
    cfg.min_track_length = 3;
    cfg.gyro_noise_density = 1.5e-4;
    cfg.accel_noise_density = 2.0e-3;
    cfg.gyro_bias_random_walk = 1.0e-5;
    cfg.accel_bias_random_walk = 1.0e-4;
    cfg.pixel_noise_std = 0.002;
    cfg.min_triangulation_deg = 2.0;
    cfg.chi2_rejection_prob = 0.95;
    cfg.enable_fej = true;

    MsckfContext* ctx = msckf_create(&cfg);
    if (!ctx) return -1;

    /* Симуляція надходження IMU */
    MsckfImuMeasurement imu;
    imu.timestamp = 100.002;
    imu.linear_accel = (MsckfVec3){0.0, 0.0, 9.81};
    imu.angular_vel = (MsckfVec3){0.0, 0.0, 0.0};
    msckf_feed_imu(ctx, &imu);

    /* Зчитування навігаційної оцінки */
    MsckfEstimate est;
    if (msckf_get_estimate(ctx, &est) == MSCKF_SUCCESS) {
        printf("Положення: X=%.3f, Y=%.3f, Z=%.3f\n", est.position.x, est.position.y, est.position.z);
    }

    msckf_destroy(ctx);
    return 0;
}
