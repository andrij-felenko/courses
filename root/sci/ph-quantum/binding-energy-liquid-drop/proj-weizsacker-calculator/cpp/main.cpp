#include <iostream>
#include <cmath>
#include <optional>
#include <iomanip>

namespace nuclear {

// Фізичні константи формули Вейцзеккера
constexpr double a_volume    = 15.75; // МеВ
constexpr double a_surface   = 17.80; // МеВ
constexpr double a_coulomb   = 0.711; // МеВ
constexpr double a_asymmetry = 23.70; // МеВ
constexpr double a_pairing   = 11.18; // МеВ

constexpr double mev_per_amu       = 931.494028;
constexpr double mass_proton_amu   = 1.00727647;
constexpr double mass_neutron_amu  = 1.00866491;

struct NucleusResult {
    int Z;
    int A;
    int N;
    double e_volume;
    double e_surface;
    double e_coulomb;
    double e_asymmetry;
    double e_pairing;
    double e_binding;
    double e_specific;
    double mass_defect_u;
    double atomic_mass_u;
};

class WeizsackerCalculator {
public:
    [[nodiscard]] static std::optional<NucleusResult> compute(int Z, int A) noexcept {
        if (Z <= 0 || A <= 0 || Z > A) {
            return std::nullopt;
        }

        const int N = A - Z;
        const double a_val = static_cast<double>(A);
        const double z_val = static_cast<double>(Z);

        const double ev = a_volume * a_val;
        const double es = -a_surface * std::pow(a_val, 2.0 / 3.0);
        const double ec = -a_coulomb * z_val * (z_val - 1.0) / std::pow(a_val, 1.0 / 3.0);
        const double ea = -a_asymmetry * std::pow(a_val - 2.0 * z_val, 2.0) / a_val;
        const double ep = computePairing(Z, N, A);

        const double eb = ev + es + ec + ea + ep;
        const double spec = eb / a_val;
        const double dm_u = eb / mev_per_amu;
        const double mass_u = z_val * mass_proton_amu + static_cast<double>(N) * mass_neutron_amu - dm_u;

        return NucleusResult{
            .Z = Z, .A = A, .N = N,
            .e_volume = ev, .e_surface = es, .e_coulomb = ec,
            .e_asymmetry = ea, .e_pairing = ep,
            .e_binding = eb, .e_specific = spec,
            .mass_defect_u = dm_u, .atomic_mass_u = mass_u
        };
    }

    [[nodiscard]] static constexpr double betaStabilityZ(int A) noexcept {
        const double a_val = static_cast<double>(A);
        return a_val / (2.0 + (a_coulomb / (2.0 * a_asymmetry)) * std::pow(a_val, 2.0 / 3.0));
    }

private:
    [[nodiscard]] static double computePairing(int Z, int N, int A) noexcept {
        if (Z % 2 == 0 && N % 2 == 0) {
            return a_pairing / std::sqrt(static_cast<double>(A));
        }
        if (Z % 2 != 0 && N % 2 != 0) {
            return -a_pairing / std::sqrt(static_cast<double>(A));
        }
        return 0.0;
    }
};

} // namespace nuclear

int main() {
    std::cout << "=== КАЛЬКУЛЯТОР ВЕЙЦЗЕККЕРА (C++20) ===\n\n";

    if (const auto res = nuclear::WeizsackerCalculator::compute(26, 56)) {
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "Нуклід: Fe-56 (Z=" << res->Z << ", A=" << res->A << ")\n";
        std::cout << "  Об'ємний доданок (E_v):      +" << res->e_volume << " МеВ\n";
        std::cout << "  Поверхневий доданок (E_s):   " << res->e_surface << " МеВ\n";
        std::cout << "  Кулонівський доданок (E_c):  " << res->e_coulomb << " МеВ\n";
        std::cout << "  Доданок асиметрії (E_a):     " << res->e_asymmetry << " МеВ\n";
        std::cout << "  Доданок спарювання (E_p):    +" << res->e_pairing << " МеВ\n";
        std::cout << "  ----------------------------------------\n";
        std::cout << "  Повна енергія зв'язку:        " << res->e_binding << " МеВ\n";
        std::cout << "  Питома енергія зв'язку:       " << res->e_specific << " МеВ/нуклон (максимум стабільності!)\n";
        std::cout << "  Дефект маси:                  " << res->mass_defect_u << " а.о.м.\n";
        std::cout << "  Z_min бета-стабільності:      " << nuclear::WeizsackerCalculator::betaStabilityZ(56) << "\n";
    }

    return 0;
}
