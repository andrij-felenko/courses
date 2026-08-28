#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <iomanip>

enum class SubstanceCategory {
    Benign,
    RohsRestricted,
    ReachSvhcCandidate
};

struct SubstanceEntry {
    std::string name;
    std::string cas_number;
    SubstanceCategory category;
    double mass_mg{0.0};
    double rohs_limit_ppm{1000.0};
    std::string rohs_exemption{}; // Порожньо, якщо винятку нема
};

struct ArticleComponent {
    std::string part_number;
    std::string description;
    double total_mass_mg{0.0};
    std::vector<SubstanceEntry> declared_substances{};
};

struct ComplianceReport {
    bool rohs_compliant{true};
    size_t scip_dossiers_required{0};
    std::vector<std::string> log_entries{};
};

class BomComplianceEngine {
public:
    static ComplianceReport evaluate(std::string_view product_name,
                                     const std::vector<ArticleComponent>& articles) {
        ComplianceReport report;
        report.log_entries.emplace_back("Аналіз матеріальної відповідності виробу: " + std::string(product_name));

        constexpr double SVHC_THRESHOLD_PPM = 1000.0; // 0.1% w/w за регламентом REACH

        for (const auto& art : articles) {
            if (art.total_mass_mg <= 0.0) {
                report.log_entries.emplace_back("[ПОМИЛКА]: Неприпустима маса деталі " + art.part_number);
                continue;
            }

            for (const auto& sub : art.declared_substances) {
                const double ppm = (sub.mass_mg / art.total_mass_mg) * 1'000'000.0;
                const double weight_percent = (sub.mass_mg / art.total_mass_mg) * 100.0;

                // 1. Перевірка лімітів RoHS
                if (sub.category == SubstanceCategory::RohsRestricted) {
                    if (ppm > sub.rohs_limit_ppm) {
                        if (!sub.rohs_exemption.empty()) {
                            report.log_entries.emplace_back(
                                "  [RoHS EXEMPT] " + art.part_number + ": " + sub.name +
                                " (" + std::to_string(ppm) + " ppm) -> Виняток " + sub.rohs_exemption);
                        } else {
                            report.log_entries.emplace_back(
                                "  [RoHS FAIL] " + art.part_number + ": " + sub.name +
                                " (" + std::to_string(ppm) + " ppm > ліміту " +
                                std::to_string(sub.rohs_limit_ppm) + " ppm)");
                            report.rohs_compliant = false;
                        }
                    }
                }

                // 2. Перевірка REACH SVHC за правилом OAOA (CJEU C-106/14)
                if (sub.category == SubstanceCategory::ReachSvhcCandidate ||
                    sub.category == SubstanceCategory::RohsRestricted) {
                    if (ppm > SVHC_THRESHOLD_PPM) {
                        report.scip_dossiers_required++;
                        report.log_entries.emplace_back(
                            "  [SCIP TRIGGER] " + art.part_number + " -> Речовина SVHC: " +
                            sub.name + " [CAS " + sub.cas_number + "] = " +
                            std::to_string(weight_percent) + "% w/w (Потрібне досьє в ECHA SCIP)");
                    }
                }
            }
        }
        return report;
    }
};

int main() {
    std::vector<ArticleComponent> bill_of_materials = {
        {
            "R0805-10K", "Чіп-резистор товстоплівковий 10 кОм", 15.0,
            {
                {"Тетрабромбісфенол А (TBBA)", "79-94-7", SubstanceCategory::ReachSvhcCandidate, 12.0, 1000.0, ""},
                {"Оксид свинцю в склі (PbO)", "1317-36-8", SubstanceCategory::RohsRestricted, 0.45, 1000.0, "7(c)-I"}
            }
        },
        {
            "SCR-M3-10", "Гвинт латунний різьбовий M3x10", 850.0,
            {
                {"Свинець (Pb) у мідному сплаві", "7439-92-1", SubstanceCategory::RohsRestricted, 25.0, 1000.0, "6(c)"}
            }
        },
        {
            "GSK-ORING-5", "Герметизуюче кільце NBR 5мм", 500.0,
            {
                {"Дибутилфталат (DBP)", "84-74-2", SubstanceCategory::RohsRestricted, 15.0, 1000.0, ""}
            }
        }
    };

    const auto report = BomComplianceEngine::evaluate("IoT Gateway Industrial", bill_of_materials);

    std::cout << "====================================================\n";
    for (const auto& line : report.log_entries) {
        std::cout << line << "\n";
    }
    std::cout << "====================================================\n";
    std::cout << "Підсумковий статус RoHS: " << (report.rohs_compliant ? "ВІДПОВІДАЄ" : "ПОРУШЕННЯ") << "\n";
    std::cout << "Необхідно сформувати SCIP досьє: " << report.scip_dossiers_required << "\n";

    return 0;
}
