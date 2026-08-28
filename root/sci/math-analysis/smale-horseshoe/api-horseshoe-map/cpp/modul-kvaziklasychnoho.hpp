namespace physics::mechanics {

struct ClassicOrbit {
    double action_S;
    double period_T;
    double lyapunov_lambda;
};

class GutzwillerSpectrumEvaluator {
public:
    [[nodiscard]] static double computeOrbitContribution(const ClassicOrbit& orbit,
                                                          double energy,
                                                          double hbar) noexcept {
        double phase = orbit.action_S / hbar;
        double stability_factor = 1.0 / (2.0 * std::sinh(orbit.lyapunov_lambda / 2.0));
        return orbit.period_T * stability_factor * std::cos(phase);
    }
};

}
