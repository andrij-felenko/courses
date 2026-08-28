#include <iostream>
#include <iomanip>
#include <vector>
#include <string_view>
#include <cmath>
#include <memory>

// Структура фізичних параметрів магнітно-м'якого матеріалу
struct MagneticMaterial {
    std::string_view name;
    double b_sat_25c;   // Індукція насичення при 25 °C (Тл)
    double b_sat_100c;  // Індукція насичення при 100 °C (Тл)
    double cm;          // Коефіцієнт Штейнмеца Cm (Вт/(м³·Гц^α·Тл^β))
    double alpha;       // Показник степеня частоти α
    double beta;        // Показник степеня індукції β
    double curie_temp;  // Точка Кюрі (°C)
};

// Структура геометрії стандартного типорозміру осердя
struct CoreGeometry {
    std::string_view part_number;
    double a_e;         // Ефективна площа перерізу (м²)
    double l_e;         // Ефективна довжина магнітної лінії (м)
    double v_e;         // Ефективний об'єм (м³)
    double a_surface;   // Площа тепловіддачі поверхні (см²)
};

// Електричні та температурні параметри робочої точки схеми
struct OperatingCondition {
    double v_in;        // Вхідна напруга (В)
    double v_out;       // Вихідна напруга (В)
    double i_out;       // Середній струм навантаження (А)
    double f_sw;        // Частота комутації (Гц)
    double l_val;       // Індуктивність (Гн)
    int turns;          // Кількість витків обмотки
    double r_wire;      // Опір проводу (Ом)
    double t_ambient;   // Температура повітря (°C)
};

// Результат моделювання
struct SimulationResult {
    double duty_cycle;
    double delta_i;
    double i_peak;
    double i_rms;
    double b_ac;
    double b_dc;
    double b_peak;
    double p_core;
    double p_copper;
    double p_total;
    double delta_temp;
    double final_temp;
    bool is_saturated;
    bool is_overheated;
};

// Обчислювальний клас симуляції силових індуктивностей
class InductorCoreSimulator {
public:
    [[nodiscard]] static SimulationResult calculate(
        const MagneticMaterial& mat,
        const CoreGeometry& core,
        const OperatingCondition& op
    ) noexcept {
        SimulationResult res{};
        
        // 1. Аналіз шпаруватості та струму
        res.duty_cycle = op.v_out / op.v_in;
        const double t_on = res.duty_cycle / op.f_sw;
        res.delta_i = (op.v_in - op.v_out) * t_on / op.l_val;
        res.i_peak = op.i_out + res.delta_i / 2.0;
        res.i_rms = std::sqrt(op.i_out * op.i_out + (res.delta_i * res.delta_i) / 12.0);
        
        // 2. Аналіз індукції
        const double delta_b = (op.l_val * res.delta_i) / (op.turns * core.a_e);
        res.b_ac = delta_b / 2.0;
        res.b_dc = (op.l_val * op.i_out) / (op.turns * core.a_e);
        res.b_peak = res.b_dc + res.b_ac;
        
        // 3. Розрахунок втрат в осерді за законом Штейнмеца
        const double p_v = mat.cm * std::pow(op.f_sw, mat.alpha) * std::pow(res.b_ac, mat.beta);
        res.p_core = p_v * core.v_e;
        
        // 4. Джоулеві втрати в обмотці
        res.p_copper = res.i_rms * res.i_rms * op.r_wire;
        res.p_total = res.p_core + res.p_copper;
        
        // 5. Тепловий режим
        const double r_th = 40.0 / std::sqrt(core.a_surface);
        res.delta_temp = res.p_total * r_th;
        res.final_temp = op.t_ambient + res.delta_temp;
        
        // 6. Перевірка обмежень надійності
        const double b_sat_limit = (res.final_temp >= 100.0) ? mat.b_sat_100c : mat.b_sat_25c;
        res.is_saturated = (res.b_peak >= b_sat_limit);
        res.is_overheated = (res.final_temp >= mat->curie_temp - 30.0 || res.final_temp > 125.0);
        
        return res;
    }
};

int main() {
    constexpr MagneticMaterial sendust{
        .name = "Sendust (Kool Mu 60u, Fe-Si-Al)",
        .b_sat_25c = 1.05,
        .b_sat_100c = 0.95,
        .cm = 32.5,
        .alpha = 1.45,
        .beta = 2.15,
        .curie_temp = 500.0
    };
    
    constexpr MagneticMaterial high_flux{
        .name = "High Flux (60u, Ni-Fe 50/50)",
        .b_sat_25c = 1.50,
        .b_sat_100c = 1.40,
        .cm = 45.0,
        .alpha = 1.40,
        .beta = 2.10,
        .curie_temp = 480.0
    };
    
    constexpr MagneticMaterial mnzn_ferrite{
        .name = "MnZn Ferrite (N87 без зазору)",
        .b_sat_25c = 0.49,
        .b_sat_100c = 0.39,
        .cm = 10.2,
        .alpha = 1.64,
        .beta = 2.68,
        .curie_temp = 210.0
    };
    
    constexpr CoreGeometry core_t106{
        .part_number = "Toroid T106",
        .a_e = 65.3e-6,      // 65.3 мм²
        .l_e = 65.4e-3,      // 65.4 мм
        .v_e = 4.27e-6,      // 4.27 см³
        .a_surface = 35.0    // 35.0 см²
    };
    
    constexpr OperatingCondition op{
        .v_in = 48.0,
        .v_out = 12.0,
        .i_out = 6.0,
        .f_sw = 100'000.0,   // 100 кГц
        .l_val = 33.0e-6,    // 33 мкГн
        .turns = 32,
        .r_wire = 0.045,     // 45 мОм
        .t_ambient = 25.0
    };
    
    std::cout << "=================================================================\n";
    std::cout << "        СИМУЛЯТОР РОБОЧОЇ ТОЧКИ МАГНІТНОГО ОСЕРДЯ ДРОСЕЛЯ        \n";
    std::cout << "=================================================================\n\n";
    
    const std::vector<MagneticMaterial> materials = { sendust, high_flux, mnzn_ferrite };
    
    for (const auto& mat : materials) {
        const auto r = InductorCoreSimulator::calculate(mat, core_t106, op);
        
        std::cout << "Матеріал осердя: " << mat.name << "\n";
        std::cout << "-----------------------------------------------------------------\n";
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "  Шпаруватість D:        " << r.duty_cycle << "\n";
        std::cout << "  Пульсація струму ΔI:   " << r.delta_i << " A (Піковий: " 
                  << r.i_peak << " A, RMS: " << r.i_rms << " A)\n";
        std::cout << "  Змінна індукція Bac:   " << r.b_ac << " Тл\n";
        std::cout << "  Постійна індукція Bdc: " << r.b_dc << " Тл\n";
        std::cout << "  Пікова індукція Bpk:   " << r.b_peak << " Тл\n";
        std::cout << "  Втрати в осерді Pcore: " << r.p_core << " Вт\n";
        std::cout << "  Джоулеві втрати Pcu:   " << r.p_copper << " Вт\n";
        std::cout << "  Сумарні втрати Ptotal: " << r.p_total << " Вт\n";
        std::cout << "  Перегрів конструкції:  +" << r.delta_temp << " °C  (Температура: " 
                  << r.final_temp << " °C)\n";
        std::cout << "  Стан насичення:        [" 
                  << (r.is_saturated ? "АВАРІЯ: МАТЕРІАЛ НАСИЧЕНО" : "НОРМА: ІНДУКЦІЯ В МЕЖАХ") << "]\n";
        std::cout << "  Стан перегріву:        [" 
                  << (r.is_overheated ? "АВАРІЯ: ТЕПЛОВИЙ ПЕРЕГРІВ" : "НОРМА: ТЕМПЕРАТУРА СТАБІЛЬНА") << "]\n\n";
    }
    
    return 0;
}
