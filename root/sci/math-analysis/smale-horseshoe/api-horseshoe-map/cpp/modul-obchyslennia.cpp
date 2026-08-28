namespace physics::mechanics {

class CorrelationDimensionAnalyzer {
public:
    [[nodiscard]] static double computeCorrelationIntegral(std::span<const Point2D> points, double r) {
        size_t count = 0;
        const size_t N = points.size();
        for (size_t i = 0; i < N; ++i) {
            for (size_t j = i + 1; j < N; ++j) {
                double dx = points[i].x - points[j].x;
                double dy = points[i].y - points[j].y;
                if (std::sqrt(dx * dx + dy * dy) < r) {
                    count++;
                }
            }
        }
        return (2.0 * count) / (N * (N - 1));
    }
};

}
