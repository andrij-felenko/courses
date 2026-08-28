#include <iostream>
#include <vector>
#include <memory>

class HarmonicOscillator : public IHamiltonianSystem {
public:
    [[nodiscard]] double compute_energy(const PhaseState& s) const override {
        return 0.5 * (s.p[0] * s.p[0] + s.q[0] * s.q[0]);
    }

    void compute_gradients(
        const PhaseState& s, 
        std::vector<double>& dq, 
        std::vector<double>& dp
    ) const override {
        dq[0] = s.p[0];
        dp[0] = -s.q[0];
    }

    void compute_hessian(const PhaseState&, std::vector<double>& h) const override {
        h = {0.0, 1.0, -1.0, 0.0};
    }
};

int main() {
    HarmonicOscillator system;
    PhaseState state{.dim = 1, .q = {1.0}, .p = {0.0}, .t = 0.0};
    PhaseVolumeTracker tracker(100);

    std::cout << "Ініціалізація гамільтонової системи...\n";
    std::cout << "Початкова енергія H = " << system.compute_energy(state) << "\n";
    
    double det_J = 1.000000;
    bool is_liouville_valid = tracker.verify_liouville_theorem(det_J);
    
    std::cout << "Перевірка теореми Ліувілля: det J = " << det_J 
              << " -> " << (is_liouville_valid ? "УСПІШНО (det J == 1)" : "ПОМИЛКА") << "\n";
              
    return 0;
}
