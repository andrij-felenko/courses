#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <regex>
#include <optional>
#include <algorithm>

struct BomRow {
    std::string designators_raw;
    int quantity{0};
    std::string mpn;
    std::string manufacturer;
    std::string footprint;
    std::string status{"Populate"};
    int line_number{0};
};

struct AuditReport {
    int error_count{0};
    int warning_count{0};
    std::vector<std::string> messages;

    void add_error(int line, std::string_view msg) {
        error_count++;
        messages.push_back("[ПОМИЛКА] Рядок " + std::to_string(line) + ": " + std::string(msg));
    }

    void add_warning(int line, std::string_view msg) {
        warning_count++;
        messages.push_back("[ПОПЕРЕДЖЕННЯ] Рядок " + std::to_string(line) + ": " + std::string(msg));
    }
};

class BomValidator {
public:
    static std::vector<std::string> parse_csv_line(std::string_view line) {
        std::vector<std::string> fields;
        std::string current;
        bool in_quotes = false;

        for (char ch : line) {
            if (ch == '"') {
                in_quotes = !in_quotes;
            } else if (ch == ',' && !in_quotes) {
                fields.push_back(trim(current));
                current.clear();
            } else {
                current += ch;
            }
        }
        fields.push_back(trim(current));
        return fields;
    }

    static std::string trim(std::string_view s) {
        auto start = s.find_first_not_of(" \t\r\n\"");
        if (start == std::string_view::npos) return "";
        auto end = s.find_last_not_of(" \t\r\n\"");
        return std::string(s.substr(start, end - start + 1));
    }

    static std::vector<std::string> split_designators(std::string_view raw) {
        std::vector<std::string> result;
        std::string current;
        for (char c : raw) {
            if (c == ',' || c == ';' || c == ' ') {
                auto t = trim(current);
                if (!t.empty()) result.push_back(t);
                current.clear();
            } else {
                current += c;
            }
        }
        auto t = trim(current);
        if (!t.empty()) result.push_back(t);
        return result;
    }

    static bool is_valid_refdes(std::string_view s) {
        static const std::regex ref_pattern("^[A-Z]{1,3}[0-9]+[A-Z]?$");
        return std::regex_match(s.data(), ref_pattern);
    }

    static bool is_dummy(std::string_view s) {
        if (s.empty()) return true;
        static const std::unordered_set<std::string_view> dummies = {
            "TBD", "N/A", "TODO", "?", "DNI", "DNP", "NONE", "UNKNOWN"
        };
        std::string upper;
        for (char c : s) upper += static_cast<char>(std::toupper(c));
        return dummies.contains(upper);
    }

    AuditReport audit_file(const std::string& path) {
        AuditReport report;
        std::ifstream file(path);
        if (!file.is_open()) {
            report.add_error(0, "Неможливо відкрити файл специфікації: " + path);
            return report;
        }

        std::unordered_map<std::string, int> seen_designators;
        std::string line;
        int line_num = 0;

        // Пропускаємо шапку
        if (std::getline(file, line)) {
            line_num++;
        }

        while (std::getline(file, line)) {
            line_num++;
            if (line.empty() || line[0] == '\r') continue;

            auto fields = parse_csv_line(line);
            if (fields.size() < 5) {
                report.add_error(line_num, "Недостатня кількість полів у рядку (" + std::to_string(fields.size()) + ")");
                continue;
            }

            BomRow row{
                .designators_raw = fields[0],
                .quantity = 0,
                .mpn = fields[2],
                .manufacturer = fields[3],
                .footprint = fields[4],
                .status = (fields.size() > 5 && !fields[5].empty()) ? fields[5] : "Populate",
                .line_number = line_num
            };

            try {
                row.quantity = std::stoi(fields[1]);
            } catch (...) {
                report.add_error(line_num, "Нечислове значення у полі кількості: '" + fields[1] + "'");
                continue;
            }

            bool is_dnp = (row.status == "DNP" || row.status == "DNI" || row.status == "NF");
            auto des_list = split_designators(row.designators_raw);

            // 1. Звірка кількості
            if (static_cast<int>(des_list.size()) != row.quantity) {
                report.add_error(line_num, "Невідповідність Qty! Заявлено " + std::to_string(row.quantity) +
                                           ", перелічено " + std::to_string(des_list.size()) +
                                           " (" + row.designators_raw + ")");
            }

            // 2. Валідація кожного RefDes
            for (const auto& des : des_list) {
                if (!is_valid_refdes(des)) {
                    report.add_error(line_num, "Невалідний синтаксис позначення: '" + des + "'");
                }
                if (auto it = seen_designators.find(des); it != seen_designators.end()) {
                    report.add_error(line_num, "Дублювання позначення '" + des + "' (раніше у рядку " + std::to_string(it->second) + ")");
                } else {
                    seen_designators[des] = line_num;
                }
            }

            // 3. Перевірка обов'язкових полів для монтованих позицій
            if (!is_dnp) {
                if (is_dummy(row.mpn)) {
                    report.add_error(line_num, "Монтована деталь (" + row.designators_raw + ") не має валідного MPN ('" + row.mpn + "')");
                }
                if (is_dummy(row.manufacturer)) {
                    report.add_error(line_num, "Монтована деталь (" + row.designators_raw + ") не має назви виробника");
                }
                if (is_dummy(row.footprint)) {
                    report.add_error(line_num, "Відсутнє посадкове місце (Footprint) для (" + row.designators_raw + ")");
                }

                // 4. Перевірка суфікса Tape & Reel для мікросхем
                if (!des_list.empty() && des_list[0].starts_with('U')) {
                    std::string mpn_upper = row.mpn;
                    for (char& c : mpn_upper) c = static_cast<char>(std::toupper(c));
                    if (!mpn_upper.ends_with("TR") && !mpn_upper.ends_with("R") && !mpn_upper.ends_with("T&R")) {
                        report.add_warning(line_num, "Мікросхема " + row.designators_raw + " (" + row.mpn + ") може не містити суфікса стрічки (Tape & Reel)");
                    }
                }
            }
        }

        return report;
    }
};
