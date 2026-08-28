#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <optional>
#include <expected>
#include <format>
#include <numeric>
#include <cstdint>

namespace pcb::diagnostics {

constexpr double CuResistivity = 1.724e-8; // Ом*м при 20°C
constexpr double CuFoil1Oz     = 35.0e-6;   // 35 мкм

enum class RailLoadType {
    HighVoltageIn,
    DigitalIo,
    MemoryVddq,
    CoreLogic,
    AnalogPll
};

enum class MeasurementStatus {
    Untested,
    HardShort,      // R < 0.05 Ом (металевий місток чи пробитий MLCC)
    OutOfSpecLow,   // R < R_min (аномальний струм витоку)
    Normal,         // Штатна норма
    HighResistance  // Можливий обрив
};

struct PowerRailSpec {
    std::string name;
    double v_nominal{0.0};       // В
    double i_max{0.0};           // А
    double c_filter_uf{0.0};     // мкФ
    RailLoadType load_type{RailLoadType::DigitalIo};
    double r_min_expected{0.0};  // Ом
    double r_typical{0.0};       // Ом
    double t_settle_sec{0.0};    // с
};

struct RailTestResult {
    double r_measured_fwd{0.0}; // Прямий вимір, Ом
    double r_measured_rev{0.0}; // Зворотний вимір, Ом
    MeasurementStatus status{MeasurementStatus::Untested};
    bool visual_polarity_ok{false};
    bool pin1_orientation_ok{false};
    bool solder_bridges_checked{false};
};

class PrePowerInspector {
public:
    explicit PrePowerInspector(std::string_view board_name, std::string_view serial_number)
        : board_name_{board_name}, serial_number_{serial_number} {}

    void add_rail(std::string_view name,
                  double v_nominal,
                  double i_max,
                  double c_filter_uf,
                  RailLoadType load_type) {
        PowerRailSpec spec{
            .name = std::string(name),
            .v_nominal = v_nominal,
            .i_max = i_max,
            .c_filter_uf = c_filter_uf,
            .load_type = load_type
        };
        calculate_thresholds(spec);
        rails_.push_back(spec);
        results_.emplace_back();
    }

    std::expected<void, std::string> record_measurement(size_t index, double r_fwd, double r_rev) {
        if (index >= rails_.size()) {
            return std::unexpected(std::format("Індекс шини {} виходить за межі діапазону", index));
        }

        auto& result = results_[index];
        const auto& spec = rails_[index];

        result.r_measured_fwd = r_fwd;
        result.r_measured_rev = r_rev;

        if (r_fwd < 0.05 || r_rev < 0.05) {
            result.status = MeasurementStatus::HardShort;
        } else if (r_fwd < spec.r_min_expected) {
            result.status = MeasurementStatus::OutOfSpecLow;
        } else {
            result.status = MeasurementStatus::Normal;
        }

        return {};
    }

    [[nodiscard]] static double calculate_kelvin_drop(double length_mm, double width_mm, double current_a) noexcept {
        if (width_mm <= 0.0) return 0.0;
        constexpr double r_sq = CuResistivity / CuFoil1Oz; // ~0.4926 мОм/sq
        const double squares = length_mm / width_mm;
        return current_a * (r_sq * squares);
    }

    void print_report() const {
        std::cout << "================================================================================\n";
        std::cout << "     ПРОТОКОЛ ПЕРЕДСТАРТОВОЇ ІНСПЕКЦІЇ ТА ДЗВІНКА РЕЙОК ЖИВЛЕННЯ ПЛАТИ          \n";
        std::cout << std::format("  Виріб: {:<20} | Серійний номер: {:<20}\n", board_name_, serial_number_);
        std::cout << "================================================================================\n";
        std::cout << std::format("{:<10} | {:<6} | {:<8} | {:<12} | {:<12} | {:<15}\n",
                                 "Рейка", "V_ном", "I_макс", "R_мін (пор)", "R_вимір (F/R)", "Статус лінії");
        std::cout << "--------------------------------------------------------------------------------\n";

        bool all_pass = true;
        for (size_t i = 0; i < rails_.size(); ++i) {
            const auto& s = rails_[i];
            const auto& r = results_[i];

            std::string_view status_view = "НЕ ВІДОМО";
            switch (r.status) {
                case MeasurementStatus::Untested:
                    status_view = "НЕ ТЕСТОВАНО";
                    all_pass = false;
                    break;
                case MeasurementStatus::HardShort:
                    status_view = "КРИТИЧНЕ КЗ (!)";
                    all_pass = false;
                    break;
                case MeasurementStatus::OutOfSpecLow:
                    status_view = "НИЗЬКИЙ ОПІР";
                    all_pass = false;
                    break;
                case MeasurementStatus::Normal:
                    status_view = "НОРМА (PASS)";
                    break;
                case MeasurementStatus::HighResistance:
                    status_view = "ВИСОКИЙ ОПІР";
                    break;
            }

            const std::string meas_str = std::format("{:.2f}/{:.2f}", r.r_measured_fwd, r.r_measured_rev);
            std::cout << std::format("{:<10} | {:>5.2f}В | {:>5.2f}А  | {:>9.2f} Ом | {:<12} | {:<15}\n",
                                     s.name, s.v_nominal, s.i_max, s.r_min_expected, meas_str, status_view);
        }
        std::cout << "================================================================================\n";

        if (all_pass) {
            std::cout << "РЕЗУЛЬТАТ: УСІ РЕЙКИ УСПІШНО ПРОЙШЛИ ПЕРЕВІРКУ. ДОЗВОЛЕНО ДИМОВИЙ ТЕСТ.\n";
        } else {
            std::cout << "УВАГА: ВИЯВЛЕНО КРИТИЧНІ АНОМАЛІЇ ОПОРУ! ПОДАВАТИ ЖИВЛЕННЯ СУВОРО ЗАБОРОНЕНО!\n";
        }
        std::cout << "================================================================================\n";
    }

private:
    static void calculate_thresholds(PowerRailSpec& spec) noexcept {
        double k_leak = 0.001;
        switch (spec.load_type) {
            case RailLoadType::HighVoltageIn:
                k_leak = 0.0001;
                spec.r_min_expected = std::max(10000.0, spec.v_nominal / (k_leak * spec.i_max));
                spec.r_typical = spec.r_min_expected * 5.0;
                break;
            case RailLoadType::DigitalIo:
                k_leak = 0.002;
                spec.r_min_expected = std::max(100.0, spec.v_nominal / (k_leak * spec.i_max));
                spec.r_typical = spec.r_min_expected * 3.0;
                break;
            case RailLoadType::MemoryVddq:
                k_leak = 0.02;
                spec.r_min_expected = std::max(10.0, spec.v_nominal / (k_leak * spec.i_max));
                spec.r_typical = 30.0;
                break;
            case RailLoadType::CoreLogic:
                k_leak = 0.10;
                spec.r_min_expected = std::max(0.15, spec.v_nominal / (k_leak * spec.i_max));
                spec.r_typical = spec.r_min_expected * 2.5;
                break;
            case RailLoadType::AnalogPll:
                k_leak = 0.001;
                spec.r_min_expected = std::max(500.0, spec.v_nominal / (k_leak * spec.i_max));
                spec.r_typical = spec.r_min_expected * 4.0;
                break;
        }

        constexpr double i_test = 200.0e-6; // 200 мкА
        constexpr double v_clamp = 0.3;     // 300 мВ
        spec.t_settle_sec = std::max(0.05, (spec.c_filter_uf * 1.0e-6 * v_clamp) / i_test);
    }

    std::string board_name_;
    std::string serial_number_;
    std::vector<PowerRailSpec> rails_;
    std::vector<RailTestResult> results_;
};

} // namespace pcb::diagnostics

int main() {
    using namespace pcb::diagnostics;

    PrePowerInspector inspector("STM32H7-ComputeModule", "SN-2026-REV-B-0042");

    inspector.add_rail("V_IN_12V",  12.0, 3.0,  220.0, RailLoadType::HighVoltageIn);
    inspector.add_rail("V_SYS_5V",   5.0, 4.0,  470.0, RailLoadType::HighVoltageIn);
    inspector.add_rail("V_IO_3V3",   3.3, 2.0,  150.0, RailLoadType::DigitalIo);
    inspector.add_rail("VDDQ_1V2",   1.2, 5.0,  680.0, RailLoadType::MemoryVddq);
    inspector.add_rail("VCORE_0V9",  0.9, 15.0, 1200.0, RailLoadType::CoreLogic);
    inspector.add_rail("VDDA_3V3",   3.3, 0.2,   47.0, RailLoadType::AnalogPll);

    // Запис результатів вимірювань
    static_cast<void>(inspector.record_measurement(0, 45000.0, 48000.0));
    static_cast<void>(inspector.record_measurement(1, 12000.0, 13500.0));
    static_cast<void>(inspector.record_measurement(2,  1850.0,  1920.0));
    static_cast<void>(inspector.record_measurement(3,    28.5,    31.0));
    static_cast<void>(inspector.record_measurement(4,     0.82,    0.85)); // 0.9V Core: 0.82 Ом (Норма!)
    static_cast<void>(inspector.record_measurement(5,  3400.0,  3450.0));

    inspector.print_report();

    const double delta_v = PrePowerInspector::calculate_kelvin_drop(25.0, 0.5, 0.2);
    std::cout << std::format("\nЛокалізація точки КЗ методом Кельвіна (I_inj = 200 мА):\n");
    std::cout << std::format("Спад напруги на відрізку міді 25 мм x 0.5 мм (1 oz): {:.3f} мВ\n", delta_v * 1000.0);

    return 0;
}
