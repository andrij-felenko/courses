namespace physics::mechanics {

class GradientMapEvaluator {
public:
    [[nodiscard]] static std::pair<double, double> computeEscapeGradient(const Point2D& pt,
                                                                          const Config& cfg) noexcept {
        return {0.0, 0.0};
    }
};

}
