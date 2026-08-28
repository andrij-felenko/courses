#include <iostream>
#include <iomanip>
#include <string_view>

enum class CircuitTopology {
    Inverting,
    NonInverting
};

struct OpAmpCircuit {
    double gbp_hz{10.0e6};       // Добуток підсилення на смугу ОП (Гц)
    double en_nv_rt_hz{10.0};    // Власний шум напруги ОП (нВ/√Гц)
    double vos_uv{1000.0};       // Вхідна напруга зміщення ОП (мкВ)
    double rin_ohm{100000.0};    // Вхідний резистор (Ом)
    double rf_ohm{10000.0};      // Резистор зворотного зв'язку (Ом)
    CircuitTopology topology{CircuitTopology::Inverting};
};

struct CircuitReport {
    double signal_gain{0.0};
    double noise_gain{0.0};
    double bandwidth_hz{0.0};
    double vos_out_uv{0.0};
    double en_out_nv_rt_hz{0.0};
};

class CircuitCalculator {
public:
    [[nodiscard]] static constexpr CircuitReport evaluate(const OpAmpCircuit& c) noexcept {
        const double ratio = c.rf_ohm / c.rin_ohm;
        
        CircuitReport report{};
        if (c.topology == CircuitTopology::Inverting) {
            report.signal_gain = -ratio;
        } else {
            report.signal_gain = 1.0 + ratio;
        }
        
        // Шумове підсилення завжди 1 + Rf/Rin
        report.noise_gain = 1.0 + ratio;
        
        // Смуга пропускання замкненого контуру: GBP / NG
        report.bandwidth_hz = c.gbp_hz / report.noise_gain;
        
        // Похибки зміщення та шуму множаться на шумове підсилення
        report.vos_out_uv = c.vos_uv * report.noise_gain;
        report.en_out_nv_rt_hz = c.en_nv_rt_hz * report.noise_gain;
        
        return report;
    }
};

int main() {
    constexpr OpAmpCircuit attenuator{
        .gbp_hz = 10.0e6,
        .en_nv_rt_hz = 10.0,
        .vos_uv = 1000.0,
        .rin_ohm = 100000.0,
        .rf_ohm = 10000.0,
        .topology = CircuitTopology::Inverting
    };
    
    constexpr auto rep = CircuitCalculator::evaluate(attenuator);
    
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Сигнальне підсилення G_сигн : " << rep.signal_gain << '\n';
    std::cout << "Шумове підсилення NG       : " << rep.noise_gain << '\n';
    std::cout << "Реальна смуга f_cl         : " << (rep.bandwidth_hz / 1e3) << " кГц\n";
    std::cout << "Вихідне зміщення Vos,out   : " << rep.vos_out_uv << " мкВ\n";
    std::cout << "Вихідний шум ОП en,out     : " << rep.en_out_nv_rt_hz << " нВ/√Гц\n";
    
    return 0;
}
