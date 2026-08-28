#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <string_view>

struct OpAmpParams {
    double gbp_hz{3.9e9};          // Добуток підсилення на смугу (3.9 ГГц)
    double en_nv_rt_hz{0.85};      // Наднизький шум напруги (0.85 нВ/√Гц)
    double in_pa_rt_hz{2.5};       // Власний шум струму (2.5 пА/√Гц)
    double vos_uv{100.0};          // Вхідна напруга зміщення (100 мкВ)
    double min_stable_ng{12.0};    // Мінімальне стабільне шумове підсилення
};

enum class Topology { Inverting, NonInverting };

struct CircuitParams {
    double rin_ohm{1000.0};        // Вхідний опір (Ом)
    double rf_ohm{500.0};          // Опір зворотного зв'язку (Ом)
    Topology topology{Topology::Inverting};
};

struct CompensationNetwork {
    double r_dummy_ohm{0.0};
    double c_dummy_f{0.0};
};

struct AnalysisResult {
    double signal_gain{0.0};
    double noise_gain_dc{0.0};
    double bandwidth_hz{0.0};
    double vos_out_uv{0.0};
    double en_out_nv_rt_hz{0.0};
    double total_noise_density_nv_rt_hz{0.0};
    double total_rms_noise_uv{0.0};
    bool is_stable{false};
    CompensationNetwork comp{};
};

class NoiseGainAnalyzer {
public:
    static constexpr double kBoltzmann = 1.380649e-23;
    static constexpr double kTemperatureKelvin = 298.15; // 25 °C

    [[nodiscard]] static AnalysisResult calculate(const OpAmpParams& op, const CircuitParams& ckt) noexcept {
        AnalysisResult res{};
        
        // 1. Сигнальне та шумове підсилення
        if (ckt.topology == Topology::Inverting) {
            res.signal_gain = -ckt.rf_ohm / ckt.rin_ohm;
        } else {
            res.signal_gain = 1.0 + (ckt.rf_ohm / ckt.rin_ohm);
        }
        res.noise_gain_dc = 1.0 + (ckt.rf_ohm / ckt.rin_ohm);

        // 2. Смуга та зміщення
        res.bandwidth_hz = op.gbp_hz / res.noise_gain_dc;
        res.vos_out_uv = op.vos_uv * res.noise_gain_dc;

        // 3. Синтез шумового бюджету
        res.en_out_nv_rt_hz = op.en_nv_rt_hz * res.noise_gain_dc;

        const double en_rf = std::sqrt(4.0 * kBoltzmann * kTemperatureKelvin * ckt.rf_ohm) * 1e9;
        const double en_rin = std::sqrt(4.0 * kBoltzmann * kTemperatureKelvin * ckt.rin_ohm) * 1e9;
        const double en_rin_out = en_rin * (ckt.rf_ohm / ckt.rin_ohm);

        const double in_a = op.in_pa_rt_hz * 1e-12;
        const double en_in_out = (in_a * ckt.rf_ohm) * 1e9;

        const double en_total_sq = (res.en_out_nv_rt_hz * res.en_out_nv_rt_hz) +
                                   (en_rf * en_rf) +
                                   (en_rin_out * en_rin_out) +
                                   (en_in_out * en_in_out);
        res.total_noise_density_nv_rt_hz = std::sqrt(en_total_sq);

        const double noise_bw = (std::numbers::pi / 2.0) * res.bandwidth_hz;
        res.total_rms_noise_uv = (res.total_noise_density_nv_rt_hz * std::sqrt(noise_bw)) * 1e-3;

        // 4. Перевірка стійкості та розрахунок R_dummy / C_dummy
        if (res.noise_gain_dc >= op.min_stable_ng) {
            res.is_stable = true;
        } else {
            res.is_stable = false;
            const double req_target = ckt.rf_ohm / (op.min_stable_ng - 1.0);
            const double g_dummy = (1.0 / req_target) - (1.0 / ckt.rin_ohm);
            
            if (g_dummy > 0.0) {
                res.comp.r_dummy_ohm = 1.0 / g_dummy;
                const double f_cross_target = op.gbp_hz / op.min_stable_ng;
                const double f_zero = f_cross_target / 10.0;
                res.comp.c_dummy_f = 1.0 / (2.0 * std::numbers::pi * res.comp.r_dummy_ohm * f_zero);
            }
        }

        return res;
    }
};

int main() {
    constexpr OpAmpParams op{
        .gbp_hz = 3.9e9,
        .en_nv_rt_hz = 0.85,
        .in_pa_rt_hz = 2.5,
        .vos_uv = 100.0,
        .min_stable_ng = 12.0
    };

    constexpr CircuitParams ckt{
        .rin_ohm = 1000.0,
        .rf_ohm = 500.0,
        .topology = Topology::Inverting
    };

    const auto r = NoiseGainAnalyzer::calculate(op, ckt);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "===================================================\n";
    std::cout << "   АНАЛІЗ ТА СИНТЕЗ КАСКАДУ НА ДЕКОМПЕНСОВАНОМУ ОП (C++)\n";
    std::cout << "===================================================\n";
    std::cout << "Підсилення сигналу G_сигн   : " << r.signal_gain << '\n';
    std::cout << "Шумове підсилення NG (DC)  : " << r.noise_gain_dc 
              << " (потрібно >= " << op.min_stable_ng << ")\n";
    std::cout << "Смуга пропускання f_cl     : " << (r.bandwidth_hz / 1e6) << " МГц\n";
    std::cout << "Вихідний зсув Vos(out)     : " << r.vos_out_uv << " мкВ\n";
    std::cout << "Власний шум ОП на виході   : " << r.en_out_nv_rt_hz << " нВ/√Гц\n";
    std::cout << "Повна вихідна густина шуму : " << r.total_noise_density_nv_rt_hz << " нВ/√Гц\n";
    std::cout << "Інтегральний RMS шум виходу: " << r.total_rms_noise_uv << " мкВ\n";
    std::cout << "Стан без корекції          : " 
              << (r.is_stable ? "СТІЙКИЙ" : "НЕСТІЙКИЙ (самозбудження!)") << '\n';

    if (!r.is_stable) {
        std::cout << "\n---------------------------------------------------\n";
        std::cout << "   ПАРАМЕТРИ ЛАНЦЮГА СТАБІЛІЗАЦІЇ (R_dummy || C_dummy)\n";
        std::cout << "---------------------------------------------------\n";
        std::cout << "Шунтувальний резистор R_dummy : " << r.comp.r_dummy_ohm << " Ом\n";
        std::cout << "Розділовий конденсатор C_dummy: " << (r.comp.c_dummy_f * 1e12) << " пФ\n";
        std::cout << "Результат: на ВЧ шумове підсилення зростає до " << op.min_stable_ng << ",\n";
        std::cout << "коефіцієнт сигналу G = " << r.signal_gain 
                  << " не змінюється, схема абсолютно стійка.\n";
    }
    std::cout << "===================================================\n";

    return 0;
}
