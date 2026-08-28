void MsckfEstimator::augmentState(double timestamp, const Vec3& p_bc, const Quat& q_bc) {
    if (window_.size() >= MaxSlidingWindow) {
        return;
    }
    
    const size_t n = window_.size();
    const size_t old_dim = ImuStateDim + n * PoseStateDim;
    const size_t new_dim = old_dim + PoseStateDim;
    
    CameraPose new_pose;
    new_pose.timestamp = timestamp;
    new_pose.pos = imu_.pos + p_bc;
    new_pose.att = imu_.att * q_bc;
    window_.push_back(new_pose);
    
    // Перебудова коваріаційної матриці зі збереженням блоків
    std::vector<double> new_cov(new_dim * new_dim, 0.0);
    
    for (size_t r = 0; r < old_dim; ++r) {
        for (size_t c = 0; c < old_dim; ++c) {
            new_cov[r * new_dim + c] = cov_matrix_[r * old_dim + c];
        }
    }
    
    // Заповнення кореляцій клонованої пози
    for (size_t r = 0; r < old_dim; ++r) {
        for (size_t c = 0; c < PoseStateDim; ++c) {
            double val = cov_matrix_[r * old_dim + c];
            new_cov[r * new_dim + (old_dim + c)] = val;
            new_cov[(old_dim + c) * new_dim + r] = val;
        }
    }
    
    for (size_t r = 0; r < PoseStateDim; ++r) {
        for (size_t c = 0; c < PoseStateDim; ++c) {
            new_cov[(old_dim + r) * new_dim + (old_dim + c)] = cov_matrix_[r * old_dim + c];
        }
    }
    
    cov_matrix_ = std::move(new_cov);
}
