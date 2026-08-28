namespace msckf {

struct EstimatorOutput {
    double timestamp{0.0};
    Vector3d position;
    Vector3d velocity;
    Quaterniond orientation;
    Vector3d gyro_bias;
    Vector3d accel_bias;
    
    Vector3d pos_std;
    Vector3d vel_std;
    Vector3d att_std;
};

struct Diagnostics {
    uint32_t current_window_size{0};
    uint32_t active_tracks_count{0};
    uint32_t updated_features{0};
    uint32_t rejected_outliers{0};
    bool is_initialized{false};
};

} // namespace msckf
