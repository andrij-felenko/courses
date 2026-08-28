namespace physics::mechanics {

struct MelnikovParams {
    double gamma{0.3};
    double delta{0.15};
    double omega{1.0};
};

class MelnikovEvaluator {
public:
    [[nodiscard]] static double computeMelnikovFunction(double t0, MelnikovParams params) noexcept {
        const double critical_ratio = (3.0 * M_PI * params.gamma) / (2.0 * std::sqrt(2.0) * params.delta);
        return -params.delta + params.gamma * std::cos(params.omega * t0) * critical_ratio;
    }
};

}
