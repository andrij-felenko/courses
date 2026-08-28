void MsckfEstimator::marginalizeOldestPose() {
    if (window_.empty()) return;
    
    const size_t old_dim = ImuStateDim + window_.size() * PoseStateDim;
    const size_t new_dim = old_dim - PoseStateDim;
    const size_t rm_offset = ImuStateDim;
    
    std::vector<double> new_cov(new_dim * new_dim, 0.0);
    size_t dst_r = 0;
    
    for (size_t src_r = 0; src_r < old_dim; ++src_r) {
        if (src_r >= rm_offset && src_r < rm_offset + PoseStateDim) continue;
        size_t dst_c = 0;
        for (size_t src_c = 0; src_c < old_dim; ++src_c) {
            if (src_c >= rm_offset && src_c < rm_offset + PoseStateDim) continue;
            new_cov[dst_r * new_dim + dst_c] = cov_matrix_[src_r * old_dim + src_c];
            dst_c++;
        }
        dst_r++;
    }
    
    cov_matrix_ = std::move(new_cov);
    window_.erase(window_.begin());
}
