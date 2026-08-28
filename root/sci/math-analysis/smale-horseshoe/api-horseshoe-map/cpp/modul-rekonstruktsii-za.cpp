namespace physics::mechanics {

struct TakensEmbeddingConfig {
    size_t delay_tau{1};
    size_t dimension_d{2};
};

class TakensReconstructor {
public:
    [[nodiscard]] static std::vector<Point2D> embedTimeSeries(std::span<const double> series,
                                                              TakensEmbeddingConfig cfg) {
        std::vector<Point2D> embedded;
        if (series.size() <= cfg.delay_tau) return embedded;

        embedded.reserve(series.size() - cfg.delay_tau);
        for (size_t i = 0; i < series.size() - cfg.delay_tau; ++i) {
            embedded.push_back(Point2D{series[i], series[i + cfg.delay_tau]});
        }
        return embedded;
    }
};

}
