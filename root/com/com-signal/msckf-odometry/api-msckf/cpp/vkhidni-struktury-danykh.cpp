namespace msckf {

struct ImuMeasurement {
    double timestamp{0.0};
    Vector3d linear_accel;
    Vector3d angular_vel;
};

struct FeaturePoint {
    uint32_t id{0};
    double u{0.0};
    double v{0.0};
};

struct FeatureFrame {
    double timestamp{0.0};
    std::vector<FeaturePoint> features;
};

} // namespace msckf
