namespace physics::mechanics {

class TheoreticalChecker {
public:
    [[nodiscard]] static bool verifyBounds(const Config& cfg) noexcept {
        return (cfg.alpha > 0.0 && cfg.alpha < 0.5 && cfg.beta > 2.0);
    }
};

}
