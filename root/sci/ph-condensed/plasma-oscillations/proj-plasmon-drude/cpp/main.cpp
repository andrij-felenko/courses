#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <iomanip>

// Параметри моделі Друде для металу:
// wp (еВ), gamma (еВ), eps_inf (безрозмірна), eps_d (довкілля)
struct DrudeParameters {
    double wp;      // плазмова частота
    double gamma;   // частота розсіяння (згасання)
    double eps_inf; // диелектрична проникність остова
    double eps_d;   // диелектрична проникність середовища
    double n_prism; // показник заломлення призми Кречмана
};

struct PlasmonPoint {
    double omega_eV;
    double eps_real;
    double eps_imag;
    double n_ref;
    double k_ext;
    double reflectivity;
    double k_spp_real;
    double kretschmann_deg;
};

class DrudePlasmonSimulator {
private:
    DrudeParameters params_;
    static constexpr double pi_const = 3.14159265358979323846;

public:
    explicit DrudePlasmonSimulator(const DrudeParameters& params) : params_(params) {}

    // Обчислення комплексної діелектричної проникності eps(omega)
    [[nodiscard]] std::complex<double> calculateEpsilon(double omega) const {
        if (omega <= 0.0) return {params_.eps_inf, 0.0};
        std::complex<double> denominator(omega * omega, params_.gamma * omega);
        return params_.eps_inf - (params_.wp * params_.wp) / denominator;
    }

    // Обчислення коефіцієнта відбивання R(omega)
    [[nodiscard]] double calculateReflectivity(std::complex<double> eps) const {
        std::complex<double> n_complex = std::sqrt(eps);
        std::complex<double> r_amplitude = (1.0 - n_complex) / (1.0 + n_complex);
        return std::norm(r_amplitude); // |r|^2
    }

    // Обчислення хвильового вектора SPP: k_spp(omega)
    [[nodiscard]] std::complex<double> calculateKSpp(double omega, std::complex<double> eps_m) const {
        std::complex<double> eps_d_comp(params_.eps_d, 0.0);
        std::complex<double> ratio = (eps_m * eps_d_comp) / (eps_m + eps_d_comp);
        return omega * std::sqrt(ratio);
    }

    // Розрахунок кута Кречмана в градусах
    [[nodiscard]] double calculateKretschmannAngle(std::complex<double> k_spp, double omega) const {
        double k0 = omega;
        double sin_theta = k_spp.real() / (k0 * params_.n_prism);
        if (sin_theta > 1.0 || sin_theta < -1.0) return 0.0; // неможливе збудження
        return std::asin(sin_theta) * (180.0 / pi_const);
    }

    // Сканування спектрального діапазону
    [[nodiscard]] std::vector<PlasmonPoint> scanSpectrum(double start_eV, double end_eV, int steps) const {
        std::vector<PlasmonPoint> results;
        results.reserve(steps);

        double step_size = (end_eV - start_eV) / (steps - 1);
        for (int i = 0; i < steps; ++i) {
            double omega_eV = start_eV + i * step_size;
            std::complex<double> eps = calculateEpsilon(omega_eV);
            std::complex<double> n_comp = std::sqrt(eps);
            double R = calculateReflectivity(eps);
            std::complex<double> k_spp = calculateKSpp(omega_eV, eps);
            double angle_deg = calculateKretschmannAngle(k_spp, omega_eV);

            results.push_back({
                omega_eV,
                eps.real(),
                eps.imag(),
                n_comp.real(),
                n_comp.imag(),
                R,
                k_spp.real(),
                angle_deg
            });
        }
        return results;
    }
};

int main() {
    // Експериментальні константи срібла (Ag) у електронвольтах (eV)
    DrudeParameters silver{
        .wp = 9.01,
        .gamma = 0.05,
        .eps_inf = 3.7,
        .eps_d = 1.0,     // вакуум/повітря
        .n_prism = 1.517 // призма BK7
    };

    DrudePlasmonSimulator simulator(silver);
    auto spectrum = simulator.scanSpectrum(1.0, 3.5, 10);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "===========================================================================================\n";
    std::cout << "  w (eV)  |   Re(eps)   |   Im(eps)   |    n    |    k    | Reflectivity R | Angle (deg)\n";
    std::cout << "===========================================================================================\n";

    for (const auto& pt : spectrum) {
        std::cout << "  " << std::setw(6) << pt.omega_eV << "  |  "
                  << std::setw(9) << pt.eps_real << "  |  "
                  << std::setw(9) << pt.eps_imag << "  |  "
                  << std::setw(7) << pt.n_ref << " | "
                  << std::setw(7) << pt.k_ext << " | "
                  << std::setw(12) << pt.reflectivity << "  | "
                  << std::setw(9) << pt.kretschmann_deg << "\n";
    }
    std::cout << "===========================================================================================\n";
    return 0;
}
