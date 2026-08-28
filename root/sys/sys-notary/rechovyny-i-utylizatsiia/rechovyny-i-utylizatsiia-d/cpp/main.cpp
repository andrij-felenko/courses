#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <iomanip>

struct MaterialSample {
    std::string part_name;
    double total_mass_mg{0.0};
    std::string substance_name;
    double substance_mass_mg{0.0};
    double rohs_limit_percent{0.1};
    bool has_exemption{false};
    std::string exemption_clause{};
};

class ComplianceValidator {
public:
    static void evaluate(const std::vector<MaterialSample>& samples) {
        std::cout << std::fixed << std::setprecision(4);

        for (const auto& item : samples) {
            if (item.total_mass_mg <= 0.0) continue;

            const double concentration_percent = (item.substance_mass_mg / item.total_mass_mg) * 100.0;
            const double concentration_ppm = concentration_percent * 10'000.0;

            std::cout << "Деталь: " << item.part_name << " | Речовина: " << item.substance_name << "\n";
            std::cout << "  Концентрація: " << concentration_percent << "% ("
                      << std::setprecision(1) << concentration_ppm << " ppm) | Ліміт: "
                      << std::setprecision(4) << item.rohs_limit_percent << "%\n";

            if (concentration_percent > item.rohs_limit_percent) {
                if (item.has_exemption) {
                    std::cout << "  -> СТАТУС: ВІДПОВІДАЄ ЗА ВИНИТКОМ " << item.exemption_clause << "\n";
                } else {
                    std::cout << "  -> СТАТУС: КРИТИЧНЕ ПОРУШЕННЯ (FAIL)!\n";
                }
            } else {
                std::cout << "  -> СТАТУС: ВІДПОВІДАЄ НОРМІ (PASS)\n";
            }

            if (concentration_percent > 0.1) {
                std::cout << "  -> SCIP: Обов'язкова нотифікація в ECHA (SVHC > 0.1% w/w)\n";
            }
            std::cout << "\n";
        }
    }
};

int main() {
    const std::vector<MaterialSample> test_items = {
        {"Bolt-M4", 1200.0, "Свинець (Pb)", 33.6, 0.1, true, "6(c)"},
        {"Gasket-EPDM", 400.0, "Фталат DEHP", 0.8, 0.1, false, ""},
        {"Connector-SMA", 2500.0, "Кадмій (Cd)", 0.15, 0.01, false, ""}
    };

    ComplianceValidator::evaluate(test_items);
    return 0;
}
