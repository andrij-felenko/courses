#include <iostream>
#include <iomanip>
#include <cmath>
#include <string_view>

namespace circuit {

struct PowerRail {
    double v_nominal{3.70};       // Номінальна напруга джерела, В
    double r_source_esr{0.08};    // ESR джерела, Ом
    double r_cable{0.22};         // Опір кабелю, Ом
    double l_cable{180e-9};       // Індуктивність кабелю, Гн
    double v_bor_limit{2.80};     // Поріг BOR, В

    [[nodiscard]] constexpr double total_resistance() const noexcept {
        return r_source_esr + r_cable;
    }
};

struct DynamicLoad {
    double i_quiescent{0.030};     // Струм спокою, А
    double motor_r_winding{2.0};   // Опір обмотки двигуна, Ом
    double motor_i_nominal{0.250}; // Робочий струм двигуна, А
    double motor_t_ramp{0.020};    // Час розгону, с

    [[nodiscard]] constexpr double stall_current(double v_supply) const noexcept {
        return (motor_r_winding > 0.0) ? (v_supply / motor_r_winding) : 0.0;
    }
};

class StabilityAnalyzer {
public:
    constexpr StabilityAnalyzer(PowerRail rail, DynamicLoad load) noexcept
        : rail_{rail}, load_{load} {}

    void analyze(double c_bulk_uf) const {
        const double c_bulk_f = c_bulk_uf * 1e-6;
        const double r_total = rail_.total_resistance();
        const double i_stall = load_.stall_current(rail_.v_nominal);
        const double i_peak = load_.i_quiescent + i_stall;
        const double v_sag = rail_.v_nominal - i_peak * r_total;

        double q_factor = 0.0;
        if (r_total > 0.0 && c_bulk_f > 0.0) {
            q_factor = (1.0 / r_total) * std::sqrt(rail_.l_cable / c_bulk_f);
        }

        std::cout << "--- C++ Аналіз стабільності живлення (C = " << c_bulk_uf << " мкФ) ---\n";
        std::cout << "  Пусковий струм: " << i_stall << " А | Статичний спад: " << (i_peak * r_total) << " В\n";
        std::cout << "  Напруга шини: " << v_sag << " В (поріг скидання BOR: " << rail_.v_bor_limit << " В)\n";
        std::cout << "  Добротність Q: " << q_factor << " (" 
                  << ((q_factor > 0.5) ? "Схильність до дзвону" : "Демпфовано") << ")\n";

        if (v_sag < rail_.v_bor_limit) {
            std::cout << "  [УВАГА] Небезпека: BOR активується, МК буде скинуто!\n";
            const double delta_v = rail_.v_nominal - rail_.v_bor_limit;
            const double c_min = (i_stall * 50e-6) / delta_v;
            std::cout << "  -> Потрібна ємність щонайменше: " << (c_min * 1e6) << " мкФ\n";
        } else {
            std::cout << "  [OK] Живлення стабільне (запас: +" << (v_sag - rail_.v_bor_limit) << " В)\n";
        }
        std::cout << "\n";
    }

private:
    PowerRail rail_;
    DynamicLoad load_;
};

} // namespace circuit

int main() {
    std::cout << std::fixed << std::setprecision(3);

    circuit::PowerRail rail{};
    circuit::DynamicLoad load{};
    circuit::StabilityAnalyzer analyzer{rail, load};

    analyzer.analyze(10.0);   // Тест із малою керамікою 10 мкФ
    analyzer.analyze(470.0);  // Тест із фільтром 470 мкФ

    return 0;
}
