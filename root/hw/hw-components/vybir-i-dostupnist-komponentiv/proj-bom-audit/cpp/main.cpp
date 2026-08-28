#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <sstream>
#include <iomanip>
#include <algorithm>

struct BomEntry {
    std::string designator;
    std::string mpn;
    std::string manufacturer;
    std::string value;
    std::string footprint;
    std::string alt_mpn;
    double rail_voltage{0.0};
    double rated_voltage{0.0};

    [[nodiscard]] bool is_capacitor() const noexcept {
        return !designator.empty() && (designator.front() == 'C' || designator.front() == 'c');
    }

    [[nodiscard]] double voltage_derating_margin() const noexcept {
        if (rail_voltage <= 0.0) return 100.0;
        return rated_voltage / rail_voltage;
    }
};

struct AuditSummary {
    std::size_t total_components{0};
    std::size_t missing_alt_count{0};
    std::size_t derating_violations{0};

    [[nodiscard]] bool is_production_ready() const noexcept {
        return derating_violations == 0 && missing_alt_count == 0;
    }
};

class BomAuditor {
public:
    static std::vector<BomEntry> parse_csv(std::string_view csv_content) {
        std::vector<BomEntry> entries;
        std::istringstream stream{std::string(csv_content)};
        std::string line;
        bool is_header = true;

        while (std::getline(stream, line)) {
            if (line.empty()) continue;
            if (is_header) {
                is_header = false;
                continue;
            }

            std::istringstream line_stream(line);
            std::string token;
            std::vector<std::string> cols;

            while (std::getline(line_stream, token, ',')) {
                if (token.size() >= 2 && token.front() == '"' && token.back() == '"') {
                    token = token.substr(1, token.size() - 2);
                }
                cols.push_back(token);
            }

            if (cols.size() >= 5 && !cols[0].empty() && !cols[1].empty()) {
                BomEntry entry;
                entry.designator = cols[0];
                entry.mpn = cols[1];
                entry.manufacturer = cols[2];
                entry.value = cols[3];
                entry.footprint = cols[4];
                if (cols.size() > 5) entry.alt_mpn = cols[5];
                if (cols.size() > 6 && !cols[6].empty()) entry.rail_voltage = std::stod(cols[6]);
                if (cols.size() > 7 && !cols[7].empty()) entry.rated_voltage = std::stod(cols[7]);
                entries.push_back(std::move(entry));
            }
        }
        return entries;
    }

    static AuditSummary audit(const std::vector<BomEntry>& entries) {
        AuditSummary summary;
        summary.total_components = entries.size();

        std::cout << "\n=== РЕЗУЛЬТАТИ ІНЖЕНЕРНОГО АУДИТУ BOM (C++) ===\n";

        for (const auto& item : entries) {
            if (item.alt_mpn.empty()) {
                std::cout << "[ПОПЕРЕДЖЕННЯ AML] Позиція " << item.designator 
                          << " (MPN: " << item.mpn << ") не має затвердженого аналога!\n";
                summary.missing_alt_count++;
            }

            if (item.is_capacitor() && item.rail_voltage > 0.0) {
                const double margin = item.voltage_derating_margin();
                if (margin < 1.5) {
                    std::cout << "[ДЕФЕКТ НАПРУГИ] Конденсатор " << item.designator 
                              << ": номінал " << item.rated_voltage << "В для шини " 
                              << item.rail_voltage << "В (запас " << std::fixed 
                              << std::setprecision(2) << margin << " < 1.50)!\n";
                    summary.derating_violations++;
                }
            }
        }

        return summary;
    }
};

int main() {
    constexpr std::string_view csv_data =
        "Designator,MPN,Manufacturer,Value,Footprint,Alt_MPN,Rail_V,Rated_V\n"
        "C1,GRM188R71E104KA01D,Murata,100nF,0603,CL10B104KB8NNNC,3.3,25.0\n"
        "C2,GRM155R60J106ME47D,Murata,10uF,0402,,5.0,6.3\n"
        "R1,RC0603FR-0710KL,Yageo,10k,0603,CRCW060310K0FKEA,3.3,50.0\n"
        "U1,STM32G030K8T6,STMicroelectronics,MCU_64K,LQFP-32,,3.3,3.6\n";

    const auto entries = BomAuditor::parse_csv(csv_data);
    const auto summary = BomAuditor::audit(entries);

    std::cout << "\n--- ПІДСУМОК АУДИТУ ---\n"
              << "Перевірено позицій: " << summary.total_components << "\n"
              << "Порушень запасу напруги: " << summary.derating_violations << "\n"
              << "Позицій без Multi-Source: " << summary.missing_alt_count << "\n";

    if (summary.is_production_ready()) {
        std::cout << "СТАТУС: BOM ЗАТВЕРДЖЕНО ДО ВИРОБНИЦТВА\n";
    } else {
        std::cout << "СТАТУС: ПОТРІБНЕ ДООПРАЦЮВАННЯ СПЕЦИФІКАЦІЇ\n";
    }

    return 0;
}
