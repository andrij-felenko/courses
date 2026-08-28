namespace physics::mechanics {

struct JacobianMatrix {
    double j00, j01, j10, j11;
};

class StabilityAnalyzer {
public:
    [[nodiscard]] static std::expected<JacobianMatrix, MappingStatus> computeJacobian(const Point2D& pt,
                                                                                      const Config& cfg) noexcept {
        if (pt.y >= 0.0 && pt.y <= cfg.alpha) {
            return JacobianMatrix{cfg.alpha, 0.0, 0.0, cfg.beta};
        }
        if (pt.y >= (1.0 - cfg.alpha) && pt.y <= 1.0) {
            return JacobianMatrix{-cfg.alpha, 0.0, 0.0, -cfg.beta};
        }
        return std::unexpected(MappingStatus::EscapedDomain);
    }
};

}
