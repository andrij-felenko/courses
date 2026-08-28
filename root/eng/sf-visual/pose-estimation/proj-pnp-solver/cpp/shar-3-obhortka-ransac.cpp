struct PnPResult { Pose pose; std::vector<int> inliers; };

// стійка до викидів поза: RANSAC над DLT + фінальне уточнення на inliers
PnPResult solvePnPRansac(const Camera& cam, const std::vector<Corr>& pts,
                         double thr = 3.0, double conf = 0.99,
                         int maxIters = 2000, unsigned seed = 0) {
    const int n = (int)pts.size();
    const int s = 6;                                    // мінімум пар для DLT
    std::mt19937 rng(seed);
    std::vector<int> idx(n);
    for (int i = 0; i < n; ++i) idx[i] = i;

    PnPResult best;
    int bestCount = -1, N = maxIters;

    for (int iter = 0; iter < N; ++iter) {
        // випадкова мінімальна вибірка — частковий Фішер–Єйтс, s без повторів
        for (int i = 0; i < s; ++i) {
            std::uniform_int_distribution<int> pick(i, n - 1);
            std::swap(idx[i], idx[pick(rng)]);
        }
        std::vector<Corr> sample;
        for (int i = 0; i < s; ++i) sample.push_back(pts[idx[i]]);
        Pose hyp = dlt(cam, sample);

        // лічимо inliers: похибка перепроєкції < поріг, і точка перед камерою
        std::vector<int> in;
        for (int i = 0; i < n; ++i) {
            Vector3d Xc = hyp.R * pts[i].X + hyp.t;
            if (Xc.z() <= 0) continue;                  // за камерою — не inlier
            Vector2d q(cam.fx * Xc.x() / Xc.z() + cam.cx,
                       cam.fy * Xc.y() / Xc.z() + cam.cy);
            if ((q - pts[i].uv).norm() < thr) in.push_back(i);
        }

        if ((int)in.size() > bestCount) {
            bestCount = (int)in.size();
            best.pose = hyp;  best.inliers = in;
            // адаптивна межа: скільки ще вибірок треба за нинішньої частки inliers
            double w = double(in.size()) / n;
            double denom = std::log(1.0 - std::pow(w, s));
            if (denom < 0.0)
                N = std::min(maxIters, (int)(std::log(1.0 - conf) / denom) + 1);
        }
    }

    // фінал: перерахунок на всіх inliers + нелінійне уточнення
    if ((int)best.inliers.size() >= s) {
        std::vector<Corr> inl;
        for (int i : best.inliers) inl.push_back(pts[i]);
        best.pose = refine(cam, inl, dlt(cam, inl));
    }
    return best;
}
