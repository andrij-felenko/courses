int main() {
    using namespace vision::geometry;

    // Істинна матриця гомографії (Ground Truth)
    Matrix3x3 H_gt{};
    H_gt.at(0, 0) = 1.15; H_gt.at(0, 1) = 0.12; H_gt.at(0, 2) = 120.0;
    H_gt.at(1, 0) = 0.08; H_gt.at(1, 1) = 1.05; H_gt.at(1, 2) = 65.0;
    H_gt.at(2, 0) = 0.0004; H_gt.at(2, 1) = 0.00015; H_gt.at(2, 2) = 1.0;

    std::vector<Point2D> src_pts, dst_pts;
    std::mt19937 rng(42);
    std::uniform_real_distribution<double> coord_dist(50.0, 950.0);
    std::normal_distribution<double> noise_dist(0.0, 0.5);

    // Генерація 60 валідних точок (inliers)
    for (size_t i = 0; i < 60; ++i) {
        Point2D p_src{ coord_dist(rng), coord_dist(rng) };
        auto p_dst = H_gt.transform(p_src);
        if (p_dst) {
            src_pts.push_back(p_src);
            dst_pts.push_back(Point2D{ p_dst->x + noise_dist(rng), p_dst->y + noise_dist(rng) });
        }
    }

    // Генерація 40 грубих викидів (outliers)
    for (size_t i = 0; i < 40; ++i) {
        src_pts.push_back(Point2D{ coord_dist(rng), coord_dist(rng) });
        dst_pts.push_back(Point2D{ coord_dist(rng), coord_dist(rng) });
    }

    RansacConfig config{
        .max_reprojection_error = 2.0,
        .max_iterations = 500,
        .confidence = 0.999
    };

    auto result = HomographyProcessor::estimateRANSAC(src_pts, dst_pts, config);

    if (result) {
        std::cout << "Оцінка успішна!\n";
        std::cout << "Кількість знайдених inliers: " << result->inlier_count << " / " << src_pts.size() << "\n";
        std::cout << "Середня похибка репроєкції: " << std::fixed << std::setprecision(4)
                  << result->mean_reprojection_error << " пікселів\n";
        std::cout << "\nВідновлена матриця H:\n";
        for (size_t r = 0; r < 3; ++r) {
            for (size_t c = 0; c < 3; ++c) {
                std::cout << std::setw(12) << std::setprecision(6) << result->H.at(r, c) << " ";
            }
            std::cout << "\n";
        }
    } else {
        std::cerr << "Помилка оцінки гомографії!\n";
    }

    return 0;
}
