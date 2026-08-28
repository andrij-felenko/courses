#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <format>
#include <optional>

enum class PcbLayer {
    Top,
    Bottom,
    Unknown
};

[[nodiscard]] constexpr std::string_view to_string(PcbLayer layer) noexcept {
    switch (layer) {
        case PcbLayer::Top: return "Top";
        case PcbLayer::Bottom: return "Bottom";
        default: return "Unknown";
    }
}

[[nodiscard]] PcbLayer parse_layer(std::string_view str) noexcept {
    if (str == "Top" || str == "T" || str == "TopLayer") return PcbLayer::Top;
    if (str == "Bottom" || str == "B" || str == "BottomLayer") return PcbLayer::Bottom;
    return PcbLayer::Unknown;
}

struct BomEntry {
    std::string refdes;
    std::string value;
    std::string footprint;
    std::string mpn;
    bool is_dnp{false};
    bool matched_in_cpl{false};
};

struct CplEntry {
    std::string refdes;
    double mid_x{0.0};
    double mid_y{0.0};
    double rotation{0.0};
    PcbLayer layer{PcbLayer::Top};
    bool matched_in_bom{false};
};

struct ValidationStats {
    std::size_t missing_in_cpl{0};
    std::size_t extra_in_cpl{0};
    std::size_t dnp_with_cpl{0};
    std::size_t invalid_rotation{0};
    std::size_t total_errors{0};
};

class AssemblyValidator {
public:
    static std::string_view trim(std::string_view s) noexcept {
        const auto start = s.find_first_not_of(" \t\r\n");
        if (start == std::string_view::npos) return {};
        const auto end = s.find_last_not_of(" \t\r\n");
        return s.substr(start, end - start + 1);
    }

    static std::string_view strip_quotes(std::string_view s) noexcept {
        if (s.size() >= 2 && s.front() == '"' && s.back() == '"') {
            return s.substr(1, s.size() - 2);
        }
        return s;
    }

    static std::vector<std::string> split_csv_line(std::string_view line) {
        std::vector<std::string> fields;
        std::string current;
        bool in_quotes = false;

        for (char ch : line) {
            if (ch == '"') {
                in_quotes = !in_quotes;
            } else if (ch == ',' && !in_quotes) {
                fields.emplace_back(strip_quotes(trim(current)));
                current.clear();
                continue;
            }
            current.push_back(ch);
        }
        fields.emplace_back(strip_quotes(trim(current)));
        return fields;
    }

    bool load_bom(const std::string& filepath) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            std::cerr << "Не вдалося відкрити BOM файл: " << filepath << '\n';
            return false;
        }

        std::string line;
        bool is_header = true;

        while (std::getline(file, line)) {
            const auto trimmed = trim(line);
            if (trimmed.empty()) continue;

            if (is_header) {
                is_header = false;
                continue;
            }

            const auto fields = split_csv_line(trimmed);
            if (fields.size() < 4) continue;

            const std::string& raw_refdes = fields[0];
            const std::string& val = fields[1];
            const std::string& footprint = fields[2];
            const std::string& mpn = fields[3];
            bool is_dnp = false;

            if (fields.size() >= 5) {
                const auto dnp_str = fields[4];
                is_dnp = (dnp_str == "1" || dnp_str == "DNP" || dnp_str == "DNI" || dnp_str == "TRUE");
            }

            // Розбиваємо групові позначення (наприклад, "R1, R2, R3")
            std::stringstream ss(raw_refdes);
            std::string single_ref;
            while (std::getline(ss, single_ref, ',')) {
                auto cleaned = std::string(strip_quotes(trim(single_ref)));
                if (!cleaned.empty()) {
                    bom_map_[cleaned] = BomEntry{
                        .refdes = cleaned,
                        .value = val,
                        .footprint = footprint,
                        .mpn = mpn,
                        .is_dnp = is_dnp,
                        .matched_in_cpl = false
                    };
                }
            }
        }
        return true;
    }

    bool load_cpl(const std::string& filepath) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            std::cerr << "Не вдалося відкрити CPL файл: " << filepath << '\n';
            return false;
        }

        std::string line;
        bool is_header = true;

        while (std::getline(file, line)) {
            const auto trimmed = trim(line);
            if (trimmed.empty()) continue;

            if (is_header) {
                is_header = false;
                continue;
            }

            const auto fields = split_csv_line(trimmed);
            if (fields.size() < 5) continue;

            try {
                cpl_list_.push_back(CplEntry{
                    .refdes = fields[0],
                    .mid_x = std::stod(fields[1]),
                    .mid_y = std::stod(fields[2]),
                    .rotation = std::stod(fields[4]),
                    .layer = parse_layer(fields[3]),
                    .matched_in_bom = false
                });
            } catch (const std::exception& e) {
                std::cerr << "Помилка парсингу рядка CPL: " << line << " (" << e.what() << ")\n";
            }
        }
        return true;
    }

    [[nodiscard]] ValidationStats validate() {
        ValidationStats stats;

        std::cout << "=================================================================\n";
        std::cout << "   ЗВІТ ВАЛІДАЦІЇ МОНТАЖНОГО ПАКЕТА (BOM <-> CPL MATCHING)\n";
        std::cout << "=================================================================\n\n";

        for (auto& c_entry : cpl_list_) {
            auto it = bom_map_.find(c_entry.refdes);
            if (it == bom_map_.end()) {
                std::cout << std::format("[ПОМИЛКА] CPL позиція '{}' відсутня в BOM (Фантомне розміщення)!\n", c_entry.refdes);
                std::cout << std::format("          Координати: (X={:.2f}, Y={:.2f}), Шар: {}, Кут: {:.1f} deg\n\n",
                                         c_entry.mid_x, c_entry.mid_y, to_string(c_entry.layer), c_entry.rotation);
                stats.extra_in_cpl++;
                stats.total_errors++;
            } else {
                c_entry.matched_in_bom = true;
                it->second.matched_in_cpl = true;

                if (it->second.is_dnp) {
                    std::cout << std::format("[ПОПЕРЕДЖЕННЯ] Позиція '{}' позначена як DNP у BOM, але присутня в CPL!\n", c_entry.refdes);
                    std::cout << std::format("               Деталь '{}' ({}) не повинна монтуватися.\n\n",
                                             it->second.value, it->second.mpn);
                    stats.dnp_with_cpl++;
                }
            }

            if (c_entry.rotation < 0.0 || c_entry.rotation >= 360.0) {
                const double normalized = std::fmod(std::fmod(c_entry.rotation, 360.0) + 360.0, 360.0);
                std::cout << std::format("[УВАГА] Позиція '{}' має ненормалізований кут: {:.2f} deg (Нормалізація -> {:.2f} deg)\n\n",
                                         c_entry.refdes, c_entry.rotation, normalized);
                stats.invalid_rotation++;
            }
        }

        for (const auto& [refdes, b_entry] : bom_map_) {
            if (!b_entry.matched_in_cpl && !b_entry.is_dnp) {
                std::cout << std::format("[ПОМИЛКА] BOM позиція '{}' відсутня в CPL файлі центроїдів!\n", refdes);
                std::cout << std::format("          Номінал: {}, Корпус: {}, MPN: {}\n\n",
                                         b_entry.value, b_entry.footprint, b_entry.mpn);
                stats.missing_in_cpl++;
                stats.total_errors++;
            }
        }

        std::cout << "-----------------------------------------------------------------\n";
        std::cout << "ПІДСУМОК ПЕРЕВІРКИ:\n";
        std::cout << std::format("  - Усього записів у BOM : {}\n", bom_map_.size());
        std::cout << std::format("  - Усього записів у CPL : {}\n", cpl_list_.size());
        std::cout << std::format("  - Пропущено в CPL      : {}\n", stats.missing_in_cpl);
        std::cout << std::format("  - Фантомних у CPL      : {}\n", stats.extra_in_cpl);
        std::cout << std::format("  - DNP із координатами  : {}\n", stats.dnp_with_cpl);
        std::cout << std::format("  - Ненормалізованих кутів: {}\n", stats.invalid_rotation);
        std::cout << std::format("  - Критичних помилок    : {}\n", stats.total_errors);
        std::cout << "-----------------------------------------------------------------\n";

        if (stats.total_errors == 0) {
            std::cout << "СТАТУС: МОНТАЖНИЙ ПАКЕТ ВАЛІДНИЙ (ГОТОВИЙ ДО ВИРОБНИЦТВА)\n";
        } else {
            std::cout << "СТАТУС: ВИЯВЛЕНО НЕВІДПОВІДНОСТІ (ПОТРІБНЕ ВИПРАВЛЕННЯ САПР)\n";
        }
        std::cout << "=================================================================\n";

        return stats;
    }

private:
    std::unordered_map<std::string, BomEntry> bom_map_;
    std::vector<CplEntry> cpl_list_;
};

int main(int argc, char* argv[]) {
    const std::string bom_path = (argc > 1) ? argv[1] : "bom.csv";
    const std::string cpl_path = (argc > 2) ? argv[2] : "cpl.csv";

    AssemblyValidator validator;

    std::cout << "Завантаження BOM: " << bom_path << " ...\n";
    if (!validator.load_bom(bom_path)) {
        return 1;
    }

    std::cout << "Завантаження CPL: " << cpl_path << " ...\n";
    if (!validator.load_cpl(cpl_path)) {
        return 1;
    }

    const auto stats = validator.validate();
    return (stats.total_errors == 0) ? 0 : 2;
}
