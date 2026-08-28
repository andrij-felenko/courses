#include <iostream>
#include <string>
#include <string_view>
#include <charconv>
#include <optional>
#include <unordered_map>
#include <algorithm>

struct Component {
    std::string refdes;
    std::string value_raw;
    std::optional<double> voltage_rating;
    bool is_dnp{false};

    [[nodiscard]] std::optional<double> parse_numeric_value() const {
        if (value_raw.empty()) return std::nullopt;

        std::string buffer;
        char multiplier_char = '\0';

        for (char c : value_raw) {
            if ((c >= '0' && c <= '9') || c == '.') {
                buffer += c;
            } else if (std::string_view("RKMGTpnumk").find(c) != std::string_view::npos && multiplier_char == '\0') {
                multiplier_char = c;
                buffer += '.'; // Замінюємо літеру-роздільник на десяткову крапку
            }
        }

        if (buffer.empty()) return std::nullopt;

        double base_val = 0.0;
        const char *begin = buffer.data();
        const char *end = buffer.data() + buffer.size();

        // Швидкий та безпечний розбір через C++17/20 from_chars
        auto [ptr, ec] = std::from_chars(begin, end, base_val);
        if (ec != std::errc{}) {
            // Обробка запису з множником на початку (наприклад "R22")
            if (!buffer.empty() && buffer[0] == '.') {
                auto [p2, ec2] = std::from_chars(begin + 1, end, base_val);
                if (ec2 != std::errc{}) return std::nullopt;
                base_val /= 10.0;
            } else {
                return std::nullopt;
            }
        }

        static const std::unordered_map<char, double> multipliers = {
            {'p', 1e-12}, {'n', 1e-9}, {'u', 1e-6}, {'m', 1e-3},
            {'R', 1.0},   {'k', 1e3},  {'K', 1e3},  {'M', 1e6},  {'G', 1e9}
        };

        double mult = 1.0;
        if (auto it = multipliers.find(multiplier_char); it != multipliers.end()) {
            mult = it->second;
        }

        return base_val * mult;
    }

    [[nodiscard]] bool validate_hygiene() const {
        const auto val = parse_numeric_value();
        if (!val.has_value()) {
            std::cerr << "[ПОМИЛКА] " << refdes << ": Некоректний номінал '" << value_raw << "'\n";
            return false;
        }

        // Правило: Конденсатори повинні мати робочу напругу
        if (!refdes.empty() && refdes[0] == 'C' && !is_dnp) {
            if (!voltage_rating.has_value() || *voltage_rating <= 0.0) {
                std::cerr << "[ПОПЕРЕДЖЕННЯ] " << refdes << ": Конденсатор без номіналу напруги!\n";
                return false;
            }
        }

        // Попередження про небезпечну десяткову крапку
        if (value_raw.find('.') != std::string::npos) {
            std::clog << "[ЗАСТЕРЕЖЕННЯ] " << refdes << ": Використання крапки у '" << value_raw 
                      << "' замість інженерного синтаксису.\n";
        }

        return true;
    }
};
