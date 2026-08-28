// уточнення пози: кроки Ґаусса–Ньютона по похибці перепроєкції
Pose refine(const Camera& cam, const std::vector<Corr>& pts, Pose P, int iters = 10) {
    for (int it = 0; it < iters; ++it) {
        Eigen::Matrix<double, 6, 6> H = Eigen::Matrix<double, 6, 6>::Zero();
        Eigen::Matrix<double, 6, 1> b = Eigen::Matrix<double, 6, 1>::Zero();
        for (const auto& c : pts) {
            Vector3d Xc = P.R * c.X + P.t;
            double z = Xc.z();
            if (z <= 1e-6) continue;                    // точка не перед камерою — пропустити
            Vector2d e(cam.fx * Xc.x() / z + cam.cx - c.uv.x(),   // нев'язка: проєкція − спостережене
                       cam.fy * Xc.y() / z + cam.cy - c.uv.y());
            Eigen::Matrix<double, 2, 3> D;              // ∂проєкція / ∂X_c
            D << cam.fx / z, 0, -cam.fx * Xc.x() / (z * z),
                 0, cam.fy / z, -cam.fy * Xc.y() / (z * z);
            Eigen::Matrix<double, 3, 6> G;              // ∂X_c / ∂ξ = [ I | −[X_c]× ]
            G.leftCols<3>()  = Matrix3d::Identity();
            G.rightCols<3>() = -skew(Xc);
            Eigen::Matrix<double, 2, 6> J = D * G;      // якобіан нев'язки (2×6)
            H += J.transpose() * J;
            b += J.transpose() * e;
        }
        Eigen::Matrix<double, 6, 1> xi = H.ldlt().solve(-b);     // H·ξ = −b
        Matrix3d dR = expSO3(xi.tail<3>());             // δω — множенням зліва, не додаванням
        P.R = dR * P.R;
        P.t = dR * P.t + xi.head<3>();
        if (xi.norm() < 1e-10) break;                   // збіглося
    }
    return P;
}
