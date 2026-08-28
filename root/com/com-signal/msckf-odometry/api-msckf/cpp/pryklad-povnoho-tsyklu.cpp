int runMsckfExample() {
    using namespace msckf;

    MsckfConfig cfg;
    cfg.body_T_cam = {0.1, 0.0, -0.05};
    cfg.max_window_size = 15;

    MsckfEngine engine(cfg);

    ImuMeasurement imu;
    imu.timestamp = 100.002;
    imu.linear_accel = {0.0, 0.0, 9.81};
    imu.angular_vel = {0.0, 0.0, 0.0};

    auto imu_res = engine.feedImu(imu);
    if (!imu_res) {
        return -1;
    }

    auto est_res = engine.getEstimate();
    if (est_res) {
        const auto& est = *est_res;
        // Використання оцінки у контурі керування
        (void)est.position;
    }

    return 0;
}
