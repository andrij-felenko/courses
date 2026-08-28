#include <iostream>
#include <iomanip>
#include <numbers>

struct ThermalCircuitConfig {
    double pcb_thickness_m{0.0016};    // Товщина плати (h), м
    double via_drill_m{0.0003};        // Діаметр отвору via (d), м
    double via_copper_thk_m{0.000025}; // Товщина металізації via (t), м
    int    via_count{16};              // Кількість отворів у матриці (N)
    double r_jc_k_w{2.0};              // Опір кристал-корпус, К/Вт
    double r_tim_k_w{3.0};             // Опір термопрокладки, К/Вт
    double r_heatsink_k_w{6.0};        // Опір радіатора, К/Вт
    double ambient_temp_c{25.0};       // Температура середовища, °C
    double power_dissipation_w{4.6};   // Потужність, що розсіюється, Вт
};

struct ThermalCircuitResult {
    double r_single_via_k_w{0.0};
    double r_via_array_k_w{0.0};
    double r_total_ja_k_w{0.0};
    double junction_temp_c{0.0};
    bool   is_safe{true};
};

class PcbThermalSolver {
public:
    static constexpr double kCopper = 385.0; // Теплопровідність міді, Вт/(м·К)

    [[nodiscard]] static constexpr ThermalCircuitResult solve(const ThermalCircuitConfig& cfg) noexcept {
        ThermalCircuitResult res{};

        // Площа поперечного перерізу мідної гільзи: A = pi * (d*t - t^2)
        const double d = cfg.via_drill_m;
        const double t = cfg.via_copper_thk_m;
        const double a_copper = std::numbers::pi * (d * t - t * t);

        // Опір одного via та масиву
        res.r_single_via_k_w = cfg.pcb_thickness_m / (kCopper * a_copper);
        res.r_via_array_k_w  = res.r_single_via_k_w / static_cast<double>(cfg.via_count);

        // Сумарний тепловий опір (додаємо розтікання у міді 3.0 К/Вт та припій 0.1 К/Вт)
        constexpr double r_pcb_extras = 3.1;
        res.r_total_ja_k_w = cfg.r_jc_k_w + res.r_via_array_k_w + r_pcb_extras + 
                             cfg.r_tim_k_w + cfg.r_heatsink_k_w;

        // Температура переходу T_J
        res.junction_temp_c = cfg.ambient_temp_c + cfg.power_dissipation_w * res.r_total_ja_k_w;
        res.is_safe = (res.junction_temp_c <= 125.0);

        return res;
    }
};

int main() {
    constexpr ThermalCircuitConfig config{
        .pcb_thickness_m     = 0.0016,
        .via_drill_m         = 0.0003,
        .via_copper_thk_m    = 0.000025,
        .via_count           = 16,
        .r_jc_k_w            = 2.0,
        .r_tim_k_w           = 3.0,
        .r_heatsink_k_w      = 6.0,
        .ambient_temp_c      = 25.0,
        .power_dissipation_w = 4.6
    };

    constexpr auto result = PcbThermalSolver::solve(config);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Одиничний via: R_th = " << result.r_single_via_k_w << " K/W\n";
    std::cout << "Матриця 16 via: R_th = " << result.r_via_array_k_w << " K/W\n";
    std::cout << "Повний опір R_th(JA): " << result.r_total_ja_k_w << " K/W\n";
    std::cout << "Температура кристала T_J: " << result.junction_temp_c << " °C (" 
              << (result.is_safe ? "НОРМА" : "ПЕРЕГРІВ!") << ")\n";

    return 0;
}
