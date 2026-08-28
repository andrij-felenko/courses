namespace physics::mechanics {

class BernoulliIsomorphismVerifier {
public:
    [[nodiscard]] static bool verifyIsomorphism(const Config& cfg) noexcept {
        return (cfg.alpha > 0.0 && cfg.alpha < 0.5 && cfg.beta > 2.0);
    }
};

}
