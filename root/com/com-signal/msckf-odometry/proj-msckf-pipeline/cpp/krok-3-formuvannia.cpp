void MsckfEstimator::updateFeature(const FeatureTrack& track) {
    const auto opt_p_G = triangulateFeature(window_, track);
    if (!opt_p_G) {
        return; // пропуск через малий паралакс
    }
    
    const Vec3 p_G = *opt_p_G;
    const size_t M = track.observations.size();
    const size_t rows = 2 * M;
    const size_t state_dim = cov_matrix_.empty() ? 0 : static_cast<size_t>(std::sqrt(cov_matrix_.size()));
    
    if (state_dim == 0) return;
    
    std::vector<double> r(rows, 0.0);
    std::vector<double> H_x(rows * state_dim, 0.0);
    
    for (size_t i = 0; i < M; ++i) {
        const size_t p_idx = track.observations[i].pose_idx;
        if (p_idx >= window_.size()) continue;
        
        const auto& pose = window_[p_idx];
        const double X_c = p_G.x - pose.pos.x;
        const double Y_c = p_G.y - pose.pos.y;
        const double Z_c = p_G.z - pose.pos.z;
        if (Z_c <= 0.1) continue;
        
        r[2 * i]     = track.observations[i].u - (X_c / Z_c);
        r[2 * i + 1] = track.observations[i].v - (Y_c / Z_c);
        
        const size_t col_offset = ImuStateDim + p_idx * PoseStateDim;
        H_x[(2 * i) * state_dim + (col_offset + 0)]     = -1.0 / Z_c;
        H_x[(2 * i) * state_dim + (col_offset + 2)]     =  X_c / (Z_c * Z_c);
        H_x[(2 * i + 1) * state_dim + (col_offset + 1)] = -1.0 / Z_c;
        H_x[(2 * i + 1) * state_dim + (col_offset + 2)] =  Y_c / (Z_c * Z_c);
    }
    
    // Застосування спроєктованої корекції Калмана
    constexpr double R_noise = 0.001;
    for (size_t i = 0; i < rows; ++i) {
        if (std::abs(r[i]) > 0.05) continue; // відсіювання викидів
        
        std::vector<double> H_row_P(state_dim, 0.0);
        double S = R_noise;
        for (size_t c = 0; c < state_dim; ++c) {
            for (size_t k = 0; k < state_dim; ++k) {
                H_row_P[c] += H_x[i * state_dim + k] * cov_matrix_[k * state_dim + c];
            }
            S += H_row_P[c] * H_x[i * state_dim + c];
        }
        
        if (S > 1e-9) {
            std::vector<double> K(state_dim, 0.0);
            for (size_t c = 0; c < state_dim; ++c) {
                K[c] = H_row_P[c] / S;
            }
            
            imu_.pos.x += K[0] * r[i];
            imu_.pos.y += K[1] * r[i];
            imu_.pos.z += K[2] * r[i];
        }
    }
}
