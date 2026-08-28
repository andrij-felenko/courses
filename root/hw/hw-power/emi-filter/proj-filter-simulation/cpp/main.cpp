#include <iostream>
#include <iomanip>
#include <complex>
#include <vector>
#include <cmath>
#include <string_view>

namespace emi {

using Complex = std::complex<double>;
constexpr double PI = 3.14159265358979323846;

// Модель LISN 50 мкГн / 50 Ом за стандартом CISPR 16
struct LisnModel {
    double l_choke = 50.0e-6; // 50 мкГн
    double r_iso   = 5.0;     // 5 Ом
    double c_coup  = 0.1e-6;  // 0.1 мкФ
    double r_meas  = 50.0;    // 50 Ом вхідний опір приймача

    [[nodiscard]] Complex impedance(double f) const {
        double w = 2.0 * PI * f;
        Complex s(0.0, w);
        Complex z_branch1 = s * l_choke + r_iso;
        Complex z_branch2 = r_meas + 1.0 / (s * c_coup);
        return (z_branch1 * z_branch2) / (z_branch1 + z_branch2);
    }
};

// Реальний конденсатор з ESR та ESL
struct RealCapacitor {
    double c   = 0.0;
    double esr = 0.0;
    double esl = 0.0;

    [[nodiscard]] Complex impedance(double f) const {
        double w = 2.0 * PI * f;
        Complex s(0.0, w);
        return esr + s * esl + 1.0 / (s * c);
    }
};

// Реальний індуктор з DCR та паразитною ємністю EPC
struct RealInductor {
    double l   = 0.0;
    double dcr = 0.0;
    double epc = 0.0; // Еквівалентна паралельна ємність

    [[nodiscard]] Complex impedance(double f) const {
        double w = 2.0 * PI * f;
        Complex s(0.0, w);
        Complex z_lr = s * l + dcr;
        if (epc <= 0.0) {
            return z_lr;
        }
        Complex y_epc = s * epc;
        return z_lr / (Complex(1.0, 0.0) + z_lr * y_epc);
    }
};

// Параметри вхідного ЕМС-фільтра
struct EmiFilterDesign {
    RealCapacitor cx1;    // Вхідний X-конденсатор
    RealCapacitor cx2;    // Вихідний X-конденсатор
    RealCapacitor cy;     // Y-конденсатор (два в схемі)
    RealInductor  l_cm;   // Синфазний дросель
    RealInductor  l_leak; // Індуктивність розсіювання (DM)
    double r_damp = 0.0;  // Резистор демпфування Міддлбрука
    double c_damp = 0.0;  // Конденсатор демпфування Міддлбрука
};

class FilterSimulator {
public:
    explicit FilterSimulator(EmiFilterDesign design)
        : design_(std::move(design)) {}

    // Розрахунок внесених втрат для диференціальної завади (DM)
    [[nodiscard]] double calculate_il_dm(double f, double r_load = 50.0) const {
        Complex z_lisn_dm = 2.0 * lisn_.impedance(f); // 2 гілки LISN послідовно
        Complex z_cx1 = design_.cx1.impedance(f);
        Complex z_cx2 = design_.cx2.impedance(f);
        Complex z_leak = 2.0 * design_.l_leak.impedance(f); // Індуктивність розсіювання в обох проводах

        // Паралельний демпфувальний ланцюжок
        double w = 2.0 * PI * f;
        Complex z_damp = design_.r_damp + 1.0 / (Complex(0.0, w) * design_.c_damp);

        // Напруга без фільтра (дільник джерело - навантаження)
        Complex v_unfiltered = r_load / (z_lisn_dm + r_load);

        // Матричний вузловий аналіз П-фільтра
        // Вузол 1 (вхід фільтра до LISN), Вузол 2 (вихід фільтра до навантаження)
        Complex y_in = 1.0 / z_lisn_dm + 1.0 / z_cx1 + 1.0 / z_leak;
        Complex y_out = 1.0 / z_leak + 1.0 / z_cx2 + 1.0 / z_damp + 1.0 / r_load;
        Complex y_m = -1.0 / z_leak;

        // Визначник системи вузлових рівнянь
        Complex det = y_in * y_out - y_m * y_m;
        // Напруга на виході при струмі одиничного джерела I_s = 1 / Z_lisn_dm
        Complex v_filtered = (1.0 / z_lisn_dm) * (-y_m) / det;

        double ratio = std::abs(v_unfiltered / v_filtered);
        return 20.0 * std::log10(std::max(ratio, 1.0e-6));
    }

    // Розрахунок внесених втрат для синфазної завади (CM)
    [[nodiscard]] double calculate_il_cm(double f, double r_cm_source = 25.0) const {
        Complex z_lisn_cm = lisn_.impedance(f) / 2.0; // 2 гілки LISN паралельно
        Complex z_cm_choke = design_.l_cm.impedance(f);
        // Два Y-конденсатори з L та N у землю підключені паралельно для CM
        RealCapacitor cy_total = design_.cy;
        cy_total.c *= 2.0;
        cy_total.esr /= 2.0;
        cy_total.esl /= 2.0;
        Complex z_cy_pair = cy_total.impedance(f);

        Complex v_unfiltered = z_lisn_cm / (r_cm_source + z_lisn_cm);

        // L-ланка: Choke послідовно + CY-паралельно
        Complex z_total_shunt = z_cy_pair;
        Complex z_ser = z_cm_choke;

        Complex v_filtered = (v_unfiltered * z_total_shunt) / 
                             (z_ser + z_total_shunt + z_lisn_cm);

        double ratio = std::abs(v_unfiltered / v_filtered);
        return 20.0 * std::log10(std::max(ratio, 1.0e-6));
    }

private:
    EmiFilterDesign design_;
    LisnModel lisn_;
};

} // namespace emi

int main() {
    using namespace emi;

    // Конфігурація компонентів промислового фільтра
    EmiFilterDesign filter{
        .cx1 = {.c = 0.47e-6, .esr = 0.015, .esl = 8.0e-9},  // 0.47 мкФ X2
        .cx2 = {.c = 0.22e-6, .esr = 0.020, .esl = 6.0e-9},  // 0.22 мкФ X2
        .cy  = {.c = 3.3e-9,  .esr = 0.050, .esl = 3.5e-9},  // 3.3 нФ Y2
        .l_cm = {.l = 4.7e-3, .dcr = 0.040, .epc = 15.0e-12}, // 4.7 мГн CMC (EPC 15 пФ)
        .l_leak = {.l = 25.0e-6, .dcr = 0.020, .epc = 3.0e-12}, // 25 мкГн розсіювання
        .r_damp = 1.0,      // 1.0 Ом демпфер Міддлбрука
        .c_damp = 2.2e-6    // 2.2 мкФ блокувальна ємність
    };

    FilterSimulator sim(filter);

    std::cout << "========================================================\n";
    std::cout << " АЧХ затухання вхідного ЕМС-фільтра (Insertion Loss)\n";
    std::cout << "========================================================\n";
    std::cout << std::setw(12) << "Частота" 
              << std::setw(16) << "IL_DM (дБ)" 
              << std::setw(16) << "IL_CM (дБ)" 
              << std::setw(14) << "Статус\n";
    std::cout << "--------------------------------------------------------\n";

    const std::vector<double> test_freqs = {
        10.0e3, 50.0e3, 100.0e3, 150.0e3, 300.0e3, 500.0e3,
        1.0e6, 2.0e6, 5.0e6, 10.0e6, 20.0e6, 30.0e6
    };

    for (double f : test_freqs) {
        double il_dm = sim.calculate_il_dm(f);
        double il_cm = sim.calculate_il_cm(f);

        std::string_view status = (il_dm >= 30.0 && il_cm >= 40.0) ? "PASS (OK)" : "MARGINAL";
        if (f < 150.0e3) status = "INFO";

        std::cout << std::setw(10) << std::fixed << std::setprecision(1) << (f / 1.0e3) << " кГц"
                  << std::setw(15) << std::setprecision(2) << il_dm
                  << std::setw(15) << std::setprecision(2) << il_cm
                  << std::setw(14) << status << "\n";
    }
    std::cout << "========================================================\n";

    return 0;
}
