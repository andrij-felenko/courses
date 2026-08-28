#include <iostream>
#include <complex>
#include <array>
#include <cmath>
#include <iomanip>
#include <numbers>

using Complex = std::complex<double>;

struct ThreePhaseSystem {
    double v_line{400.0};          // Лінійна напруга (В)
    double f_hz{50.0};             // Частота (Гц)
    Complex z_a{10.0, 0.0};        // Фаза A: R = 10 Ом
    Complex z_b{15.0, 10.0};       // Фаза B: R = 15 Ом, XL = 10 Ом
    Complex z_c{20.0, -8.0};       // Фаза C: R = 20 Ом, XC = 8 Ом
    Complex z_n{1.2, 0.0};         // Опір нейтралі R_N = 1.2 Ом
    bool has_neutral{true};        // Наявність нейтрального проводу
};

struct ThreePhaseResult {
    std::array<Complex, 3> u_source{};
    Complex u_n{0.0, 0.0};
    std::array<Complex, 3> u_load{};
    std::array<Complex, 3> i_phase{};
    Complex i_n{0.0, 0.0};
    std::array<double, 3> p_phase{};
    std::array<double, 3> q_phase{};
    double p_total{0.0};
    double q_total{0.0};
    double s_total{0.0};
};

class ThreePhaseCalculator {
public:
    [[nodiscard]] static ThreePhaseResult solve_star(const ThreePhaseSystem& sys) {
        ThreePhaseResult res;
        const double v_ph = sys.v_line / std::sqrt(3.0);
        
        // 1. Формування комплексних ЕРС джерела
        res.u_source[0] = Complex{v_ph, 0.0};
        res.u_source[1] = std::polar(v_ph, -2.0 * std::numbers::pi / 3.0);
        res.u_source[2] = std::polar(v_ph, 2.0 * std::numbers::pi / 3.0);
        
        // 2. Обчислення комплексних провідностей фаз Y = 1 / Z
        const std::array<Complex, 3> y_phase = {
            1.0 / sys.z_a,
            1.0 / sys.z_b,
            1.0 / sys.z_c
        };
        
        // 3. Обчислення зміщення нейтралі за формулою Мілмана
        if (sys.has_neutral) {
            const Complex y_n = 1.0 / sys.z_n;
            const Complex num = res.u_source[0] * y_phase[0] +
                                res.u_source[1] * y_phase[1] +
                                res.u_source[2] * y_phase[2];
            const Complex den = y_phase[0] + y_phase[1] + y_phase[2] + y_n;
            res.u_n = num / den;
            res.i_n = res.u_n * y_n;
        } else {
            const Complex num = res.u_source[0] * y_phase[0] +
                                res.u_source[1] * y_phase[1] +
                                res.u_source[2] * y_phase[2];
            const Complex den = y_phase[0] + y_phase[1] + y_phase[2];
            res.u_n = num / den;
            res.i_n = Complex{0.0, 0.0};
        }
        
        // 4. Розрахунок фазних напруг, струмів та потужностей
        for (std::size_t k = 0; k < 3; ++k) {
            res.u_load[k] = res.u_source[k] - res.u_n;
            res.i_phase[k] = res.u_load[k] * y_phase[k];
            
            const Complex s_k = res.u_load[k] * std::conj(res.i_phase[k]);
            res.p_phase[k] = s_k.real();
            res.q_phase[k] = s_k.imag();
            
            res.p_total += res.p_phase[k];
            res.q_total += res.q_phase[k];
        }
        
        res.s_total = std::hypot(res.p_total, res.q_total);
        return res;
    }
};

void print_result_cpp(const ThreePhaseResult& r) {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "===================================================\n";
    std::cout << "  РЕЗУЛЬТАТИ СИМУЛЯЦІЇ ТРИФАЗНОГО КОЛА (C++20)\n";
    std::cout << "===================================================\n";
    std::cout << "Зміщення нейтралі UN: " << std::abs(r.u_n) << " V, кут: " 
              << std::arg(r.u_n) * 180.0 / std::numbers::pi << " deg\n";
    std::cout << "Струм у нейтралі  IN: " << std::abs(r.i_n) << " A, кут: " 
              << std::arg(r.i_n) * 180.0 / std::numbers::pi << " deg\n";
    std::cout << "---------------------------------------------------\n";
    
    const std::array<char, 3> names{'A', 'B', 'C'};
    for (std::size_t i = 0; i < 3; ++i) {
        std::cout << "Фаза " << names[i] << ": U' = " << std::abs(r.u_load[i])
                  << " V, I = " << std::abs(r.i_phase[i])
                  << " A, P = " << r.p_phase[i]
                  << " W, Q = " << r.q_phase[i] << " VAR\n";
    }
    std::cout << "---------------------------------------------------\n";
    std::cout << "Повна активна потужність   P_total: " << r.p_total << " W\n";
    std::cout << "Повна реактивна потужність Q_total: " << r.q_total << " VAR\n";
    std::cout << "Повна потужність системи   S_total: " << r.s_total << " VA\n";
    std::cout << "===================================================\n";
}

int main() {
    const ThreePhaseSystem sys{
        .v_line = 400.0,
        .f_hz = 50.0,
        .z_a = Complex{10.0, 0.0},
        .z_b = Complex{15.0, 10.0},
        .z_c = Complex{20.0, -8.0},
        .z_n = Complex{1.2, 0.0},
        .has_neutral = true
    };
    
    const ThreePhaseResult r = ThreePhaseCalculator::solve_star(sys);
    print_result_cpp(r);
    return 0;
}
