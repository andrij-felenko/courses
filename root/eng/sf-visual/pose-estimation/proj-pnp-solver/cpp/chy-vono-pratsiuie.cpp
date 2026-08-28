#include <iostream>
int main() {
    Camera cam{800, 800, 320, 240};
    Pose gt{ expSO3(Vector3d(0.10, -0.20, 0.15)), Vector3d(0.2, -0.1, 4.0) };  // істина

    std::mt19937 rng(42);
    std::normal_distribution<double> noise(0.0, 0.5);          // 0.5 пікселя шуму
    std::uniform_real_distribution<double> u(-1, 1), pix(0, 640);
    std::vector<Corr> pts;
    for (int i = 0; i < 60; ++i) {
        Vector3d X(u(rng), u(rng), u(rng));
        Vector2d uv = project(cam, gt, X) + Vector2d(noise(rng), noise(rng));
        if (i % 5 == 0) uv = Vector2d(pix(rng), pix(rng));     // 20% викидів
        pts.push_back({X, uv});
    }

    PnPResult r = solvePnPRansac(cam, pts);
    std::cout << "inliers: " << r.inliers.size() << " / " << pts.size() << "\n";
    std::cout << "|Δt| = " << (r.pose.t - gt.t).norm() << " м\n";
    std::cout << "|ΔR| = "
              << Eigen::AngleAxisd(r.pose.R * gt.R.transpose()).angle() << " рад\n";
    return 0;
}
