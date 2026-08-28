#include <iostream>
#include <iomanip>
#include <cmath>
#include <array>
#include <optional>
#include <expected>
#include <string_view>

namespace i2c {

enum class BusMode {
    Standard,   // 100 kHz, tr_max = 1000 ns, Cb_max = 400 pF, Iol = 3 mA
    Fast,       // 400 kHz, tr_max = 300 ns,  Cb_max = 400 pF, Iol = 3 mA
    FastPlus    // 1 MHz,   tr_max = 120 ns,  Cb_max = 550 pF, Iol = 20 mA
};

struct BusConfig {
    double vdd_volts{3.3};
    BusMode mode{BusMode::Fast};
    int chip_count{5};
    double pcb_trace_length_cm{20.0};
    double cable_length_m{0.8};
    int connector_count{2};
};

struct CalculationResult {
    double total_capacitance_pf{0.0};
    double rp_min_ohms{0.0};
    double rp_max_ohms{0.0};
    double rp_recommended_ohms{0.0};
    double actual_rise_time_ns{0.0};
    double static_power_mw{0.0};
    bool exceeds_standard_cb{false};
};

enum class CalculationError {
    InvalidVoltage,
    ClosedDesignWindow,
    ExcessiveCapacitance
};

class PullupCalculator {
public:
    static constexpr double C_PIN_PER_CHIP_PF = 10.0;
    static constexpr double C_PCB_PER_CM_PF   = 1.3;
    static constexpr double C_CABLE_PER_M_PF  = 75.0;
    static constexpr double C_CONNECTOR_PF    = 2.0;
    static constexpr double LN_7_3            = 0.847297860387;

    static constexpr std::array<double, 24> E24_SERIES = {
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
    };

    static std::expected<CalculationResult, CalculationError> calculate(const BusConfig& cfg) noexcept {
        if (cfg.vdd_volts <= 0.0) {
            return std::unexpected(CalculationError::InvalidVoltage);
        }

        CalculationResult res;
        res.total_capacitance_pf = (cfg.chip_count * C_PIN_PER_CHIP_PF) +
                                   (cfg.pcb_trace_length_cm * C_PCB_PER_CM_PF) +
                                   (cfg.cable_length_m * C_CABLE_PER_M_PF) +
                                   (cfg.connector_count * C_CONNECTOR_PF);

        double tr_max_ns = 1000.0;
        double cb_limit_pf = 400.0;
        double iol_max_amps = 0.003;
        double vol_max_volts = (cfg.vdd_volts <= 2.0) ? (0.2 * cfg.vdd_volts) : 0.4;

        switch (cfg.mode) {
            case BusMode::Standard:
                tr_max_ns = 1000.0;
                cb_limit_pf = 400.0;
                iol_max_amps = 0.003;
                break;
            case BusMode::Fast:
                tr_max_ns = 300.0;
                cb_limit_pf = 400.0;
                iol_max_amps = 0.003;
                break;
            case BusMode::FastPlus:
                tr_max_ns = 120.0;
                cb_limit_pf = 550.0;
                iol_max_amps = 0.020;
                break;
        }

        res.exceeds_standard_cb = (res.total_capacitance_pf > cb_limit_pf);
        res.rp_min_ohms = (cfg.vdd_volts - vol_max_volts) / iol_max_amps;

        const double cb_farads = res.total_capacitance_pf * 1e-12;
        const double tr_max_sec = tr_max_ns * 1e-9;
        res.rp_max_ohms = tr_max_sec / (LN_7_3 * cb_farads);

        if (res.rp_min_ohms > res.rp_max_ohms) {
            return std::unexpected(CalculationError::ClosedDesignWindow);
        }

        auto e24_opt = select_e24_value(res.rp_min_ohms, res.rp_max_ohms);
        res.rp_recommended_ohms = e24_opt.value_or((res.rp_min_ohms + res.rp_max_ohms) / 2.0);

        res.actual_rise_time_ns = LN_7_3 * res.rp_recommended_ohms * cb_farads * 1e9;
        const double delta_v = cfg.vdd_volts - vol_max_volts;
        res.static_power_mw = (delta_v * delta_v / res.rp_recommended_ohms) * 1000.0;

        return res;
    }

private:
    static constexpr std::optional<double> select_e24_value(double r_min, double r_max) noexcept {
        const double target = r_min * 1.25;
        double best_val = -1.0;
        double min_diff = 1e9;

        for (int dec = 1; dec <= 5; ++dec) {
            double mult = 1.0;
            for (int d = 0; d < dec; ++d) mult *= 10.0;

            for (double mantissa : E24_SERIES) {
                const double candidate = mantissa * mult;
                const double worst_low = candidate * 0.95;
                const double worst_high = candidate * 1.05;

                if (worst_low >= r_min && worst_high <= r_max) {
                    const double diff = std::abs(candidate - target);
                    if (diff < min_diff) {
                        min_diff = diff;
                        best_val = candidate;
                    }
                }
            }
        }

        if (best_val > 0.0) {
            return best_val;
        }
        return std::nullopt;
    }
};

} // namespace i2c

int main() {
    i2c::BusConfig config{
        .vdd_volts = 3.3,
        .mode = i2c::BusMode::Fast,
        .chip_count = 5,
        .pcb_trace_length_cm = 20.0,
        .cable_length_m = 0.8,
        .connector_count = 2
    };

    auto calc_res = i2c::PullupCalculator::calculate(config);

    if (calc_res) {
        const auto& r = *calc_res;
        std::cout << "=== Результати розрахунку шини I2C (C++20) ===\n";
        std::cout << std::fixed << std::setprecision(1);
        std::cout << "Сумарна ємність Cb:      " << r.total_capacitance_pf << " пФ\n";
        std::cout << "Перевищення ліміту Cb:   " << (r.exceeds_standard_cb ? "ТАК (НЕБЕЗПЕЧНО)" : "НІ") << "\n";
        std::cout << "Діапазон підтяжки:       [" << std::setprecision(0) << r.rp_min_ohms
                  << " Ом ... " << r.rp_max_ohms << " Ом]\n";
        std::cout << "Рекомендований номінал:  " << r.rp_recommended_ohms << " Ом (E24)\n";
        std::cout << std::setprecision(1);
        std::cout << "Очікуваний час tr:       " << r.actual_rise_time_ns << " нс (ліміт: 300 нс)\n";
        std::cout << std::setprecision(2);
        std::cout << "Статична потужність:     " << r.static_power_mw << " мВт на лінію\n";
    } else {
        std::cerr << "Помилка розрахунку: вікно допустимих значень замкнене!\n";
    }

    return 0;
}
