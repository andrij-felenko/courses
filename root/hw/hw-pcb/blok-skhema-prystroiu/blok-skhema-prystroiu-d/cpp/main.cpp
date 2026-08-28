#include <iostream>
#include <vector>
#include <string_view>
#include <format>
#include <expected>
#include <cstdint>

namespace hw::power {

enum class RegulatorType : uint8_t {
    Buck,
    Ldo,
    IsolatedDcDc
};

struct PowerRail {
    std::string_view name;
    RegulatorType type;
    float v_in;          // Вхідна напруга, В
    float v_out;         // Вихідна напруга, В
    float i_load_max;    // Максимальний струм навантаження, А
    float i_limit;       // Паспортний ліміт струму регулятора, А
    float efficiency;    // ККД для DC-DC
    float theta_ja;      // Тепловий опір кристал-середовище, °C/Вт
};

struct RailMetrics {
    float power_out_w{0.0f};
    float power_loss_w{0.0f};
    float temp_junction_c{0.0f};
};

enum class ValidationError : uint8_t {
    OverCurrent,
    OverTemperature,
    Both
};

class PowerRailValidator {
public:
    constexpr explicit PowerRailValidator(float ambient_temperature_c = 60.0f) noexcept
        : ambient_temp_{ambient_temperature_c} {}

    [[nodiscard]] std::expected<RailMetrics, ValidationError> validate(const PowerRail& rail) const noexcept {
        RailMetrics metrics;
        metrics.power_out_w = rail.v_out * rail.i_load_max;

        if (rail.type == RegulatorType::Ldo) {
            metrics.power_loss_w = (rail.v_in - rail.v_out) * rail.i_load_max;
        } else {
            if (rail.efficiency > 0.01f) {
                const float p_in = metrics.power_out_w / rail.efficiency;
                metrics.power_loss_w = p_in - metrics.power_out_w;
            } else {
                metrics.power_loss_w = metrics.power_out_w * 0.2f;
            }
        }

        metrics.temp_junction_c = ambient_temp_ + (metrics.power_loss_w * rail.theta_ja);

        const bool overcurrent = (rail.i_load_max > rail.i_limit);
        const bool overheated = (metrics.temp_junction_c > 125.0f);

        if (overcurrent && overheated) {
            return std::unexpected(ValidationError::Both);
        }
        if (overcurrent) {
            return std::unexpected(ValidationError::OverCurrent);
        }
        if (overheated) {
            return std::unexpected(ValidationError::OverTemperature);
        }

        return metrics;
    }

private:
    float ambient_temp_;
};

} // namespace hw::power

int main() {
    using namespace hw::power;

    constexpr float ambient_temp = 60.0f;
    const PowerRailValidator validator{ambient_temp};

    const std::vector<PowerRail> rails = {
        {"24V->5V Buck",    RegulatorType::Buck,         24.0f, 5.0f, 2.50f, 3.00f, 0.91f, 35.0f},
        {"5V->3.3V Buck",   RegulatorType::Buck,          5.0f, 3.3f, 1.50f, 2.00f, 0.94f, 45.0f},
        {"5V->1.2V Core",   RegulatorType::Buck,          5.0f, 1.2f, 1.20f, 1.50f, 0.88f, 50.0f},
        {"5V->3.3V LDO",    RegulatorType::Ldo,           5.0f, 3.3f, 0.15f, 0.30f, 0.66f, 62.0f},
        {"5V->5V_ISO DCDC", RegulatorType::IsolatedDcDc, 5.0f, 5.0f, 0.20f, 0.25f, 0.78f, 70.0f}
    };

    std::cout << "=== Звіт валідації бюджету живлення блок-схеми (C++20) ===\n";
    for (const auto& rail : rails) {
        auto result = validator.validate(rail);
        if (result.has_value()) {
            const auto& m = result.value();
            std::cout << std::format("[{:16}] P_out = {:5.2f} Вт | P_loss = {:5.2f} Вт | T_j = {:5.1f} °C -> [НОРМА]\n",
                                     rail.name, m.power_out_w, m.power_loss_w, m.temp_junction_c);
        } else {
            std::cout << std::format("[{:16}] [ПОМИЛКА ВАЛІДАЦІЇ]\n", rail.name);
        }
    }

    return 0;
}
