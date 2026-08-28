std::optional<Vec3> triangulateFeature(
    std::span<const CameraPose> window,
    const FeatureTrack& track) 
{
    if (track.observations.size() < 2) {
        return std::nullopt;
    }
    
    std::array<std::array<double, 3>, 3> A{};
    std::array<double, 3> b{};
    
    for (const auto& obs : track.observations) {
        if (obs.pose_idx >= window.size()) continue;
        const auto& pose = window[obs.pose_idx];
        
        const double norm2 = obs.u * obs.u + obs.v * obs.v + 1.0;
        const std::array<double, 3> d = { obs.u, obs.v, 1.0 };
        const std::array<double, 3> p = { pose.pos.x, pose.pos.y, pose.pos.z };
        
        for (size_t r = 0; r < 3; ++r) {
            for (size_t c = 0; c < 3; ++c) {
                const double proj = (r == c ? 1.0 : 0.0) - (d[r] * d[c] / norm2);
                A[r][c] += proj;
                b[r] += proj * p[c];
            }
        }
    }
    
    const double det = A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) -
                       A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0]) +
                       A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]);
                       
    if (std::abs(det) < 1e-6) {
        return std::nullopt; // невизначена глибина через брак паралаксу
    }
    
    Vec3 result;
    result.x = (b[0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) -
                A[0][1] * (b[1] * A[2][2] - A[1][2] * b[2]) +
                A[0][2] * (b[1] * A[2][1] - A[1][1] * b[2])) / det;
                
    result.y = (A[0][0] * (b[1] * A[2][2] - A[1][2] * b[2]) -
                b[0] * (A[1][0] * A[2][2] - A[1][2] * A[2][0]) +
                A[0][2] * (A[1][0] * b[2] - b[1] * A[2][0])) / det;
                
    result.z = (A[0][0] * (A[1][1] * b[2] - b[1] * A[2][1]) -
                A[0][1] * (A[1][0] * b[2] - b[1] * A[2][0]) +
                b[0] * (A[1][0] * A[2][1] - A[1][1] * A[2][0])) / det;
                
    return result;
}
