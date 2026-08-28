// strapping_check.cpp - об'єктно-орієнтована валідація strapping-пінів на C++20
#include <iostream>
#include <string_view>
#include <vector>
#include <format>

enum class PullMode {
    None,
    UpVcc,
    DownGnd
};

struct StrappingPin {
    std::string_view pin_name;
    PullMode pull;
    bool expected_high;
    std::string_view description;
};

class StrappingAuditor {
public:
    explicit StrappingAuditor(std::vector<StrappingPin> pins)
        : pins_(std::move(pins)) {}

    [[nodiscard]] bool run_audit() const {
        std::cout << "=== АУДИТ КОНФІГУРАЦІЙНИХ ВИВОДІВ (C++20) ===\n";
        bool success = true;

        for (const auto& [name, pull, expected_high, desc] : pins_) {
            std::cout << "Пін " << name << " [" << desc << "]: ";

            if (pull == PullMode::None) {
                std::cout << "[ПОМИЛКА] Пін не має апаратної підтяжки!\n";
                success = false;
                continue;
            }

            bool actual_high = (pull == PullMode::UpVcc);
            if (actual_high == expected_high) {
                std::cout << "[OK] Рівень коректний ("
                          << (actual_high ? "HIGH" : "LOW") << ")\n";
            } else {
                std::cout << "[КРИТИЧНО] Помилка конфігурації! Очікується "
                          << (expected_high ? "HIGH" : "LOW") << ", підтягнуто до "
                          << (actual_high ? "VCC" : "GND") << "\n";
                success = false;
            }
        }
        return success;
    }

private:
    std::vector<StrappingPin> pins_;
};

int main() {
    std::vector<StrappingPin> config = {
        {"GPIO0",  PullMode::UpVcc,   true,  "Flash Boot Mode"},
        {"GPIO2",  PullMode::DownGnd, false, "Download Boot Mode Inhibitor"},
        {"GPIO12", PullMode::DownGnd, false, "Flash Voltage 3.3V Selector"},
        {"GPIO15", PullMode::UpVcc,   true,  "Silent Boot Logging"}
    };

    StrappingAuditor auditor(std::move(config));
    bool result = auditor.run_audit();

    std::cout << "\nПідсумок аудиту: " << (result ? "СХВАЛЕНО" : "ВІДХИЛЕНО") << '\n';
    return result ? 0 : 1;
}
