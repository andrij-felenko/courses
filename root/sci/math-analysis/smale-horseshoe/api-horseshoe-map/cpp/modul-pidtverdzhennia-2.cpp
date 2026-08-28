namespace physics::mechanics {

class ConeFieldVerifier {
public:
    [[nodiscard]] static bool verifyConeInvariance(const Config& cfg) noexcept {
        return (cfg.alpha > 0.0 && cfg.alpha < 0.5 && cfg.beta > 2.0);
    }
};

}
