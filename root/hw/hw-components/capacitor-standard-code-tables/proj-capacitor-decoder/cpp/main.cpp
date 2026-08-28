#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <charconv>
#include <cmath>
#include <iomanip>
#include <cctype>
#include <sstream>
#include <array>
#include <algorithm>

namespace capdecoder {

enum class DielectricClass {
    Unknown,
    ClassI,      // C0G / NP0
    ClassII,     // X7R, X5R
    ClassIII,    // Y5V, Z5U
    Electrolytic
};

struct ToleranceSpec {
    char code{'\0'};
    bool is_absolute{false}; // true = pF, false = %
    double plus{0.0};
    double minus{0.0};
};

struct TempClassSpec {
    std::string code;
    DielectricClass dielectric{DielectricClass::Unknown};
    int min_celsius{0};
    int max_celsius{0};
    double max_drift_pct{0.0};
};

struct CapacitorSpec {
    double capacitance_farads{0.0};
    double capacitance_pf{0.0};
    std::string formatted_value;
    std::optional<ToleranceSpec> tolerance;
    std::optional<double> rated_voltage;
    std::string voltage_code;
    std::optional<TempClassSpec> temp_class;
    double nearest_e24_nominal{0.0};
    double e24_error_pct{0.0};
};

class CapacitorParser {
public:
    static constexpr std::array<double, 24> E24_TABLE = {
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
    };

    static std::optional<CapacitorSpec> parse(std::string_view input) {
        if (input.empty()) return std::nullopt;

        auto tokens = tokenize(input);
        if (tokens.empty()) return std::nullopt;

        CapacitorSpec spec;
        char extracted_tol{'\0'};

        // 1. Перший токен завжди визначає номінальну ємність
        auto cap_pf = parse_capacitance(tokens[0], extracted_tol);
        if (!cap_pf.has_value()) return std::nullopt;

        spec.capacitance_pf = *cap_pf;
        spec.capacitance_farads = spec.capacitance_pf * 1e-12;
        spec.formatted_value = format_capacitance(spec.capacitance_pf);

        if (extracted_tol != '\0') {
            spec.tolerance = parse_tolerance(extracted_tol, spec.capacitance_pf);
        }

        // 2. Послідовна обробка додаткових токенів
        for (size_t i = 1; i < tokens.size(); ++i) {
            std::string_view tok = tokens[i];

            if (tok.size() == 1 && !spec.tolerance.has_value() && std::isalpha(static_cast<unsigned char>(tok[0]))) {
                auto tol = parse_tolerance(tok[0], spec.capacitance_pf);
                if (tol.has_value()) {
                    spec.tolerance = tol;
                    continue;
                }
            }

            if (!spec.temp_class.has_value()) {
                auto tc = parse_temp_class(tok);
                if (tc.has_value()) {
                    spec.temp_class = tc;
                    continue;
                }
            }

            if (!spec.rated_voltage.has_value()) {
                auto volt = parse_voltage(tok);
                if (volt.has_value()) {
                    spec.rated_voltage = volt;
                    spec.voltage_code = std::string(tok);
                    continue;
                }
            }
        }

        validate_e_series(spec);
        return spec;
    }

private:
    static void validate_e_series(CapacitorSpec &spec) {
        if (spec.capacitance_pf <= 0.0) return;
        double exp_val = std::floor(std::log10(spec.capacitance_pf));
        double scale = std::pow(10.0, exp_val);
        double mantissa = spec.capacitance_pf / scale;

        auto it = std::min_element(E24_TABLE.begin(), E24_TABLE.end(), [mantissa](double a, double b) {
            return std::abs(a - mantissa) < std::abs(b - mantissa);
        });

        spec.nearest_e24_nominal = (*it) * scale;
        spec.e24_error_pct = (std::abs(spec.capacitance_pf - spec.nearest_e24_nominal) / spec.nearest_e24_nominal) * 100.0;
    }

    static std::vector<std::string_view> tokenize(std::string_view str) {
        std::vector<std::string_view> tokens;
        size_t start = 0;
        while (start < str.size()) {
            while (start < str.size() && (std::isspace(static_cast<unsigned char>(str[start])) || str[start] == ',')) {
                ++start;
            }
            if (start >= str.size()) break;
            size_t end = start;
            while (end < str.size() && !std::isspace(static_cast<unsigned char>(str[end])) && str[end] != ',') {
                ++end;
            }
            tokens.push_back(str.substr(start, end - start));
            start = end;
        }
        return tokens;
    }

    static std::string format_capacitance(double pf) {
        std::ostringstream oss;
        oss << std::setprecision(4);
        if (pf >= 1e6) {
            oss << (pf / 1e6) << " uF";
        } else if (pf >= 1e3) {
            oss << (pf / 1e3) << " nF";
        } else {
            oss << pf << " pF";
        }
        return oss.str();
    }

    static std::optional<double> parse_capacitance(std::string_view tok, char &out_tol) {
        if (tok.empty()) return std::nullopt;
        out_tol = '\0';

        char last = static_cast<char>(std::toupper(static_cast<unsigned char>(tok.back())));
        std::string_view num_part = tok;
        if (std::isalpha(static_cast<unsigned char>(last)) && last != 'R' && last != 'P' && last != 'N' && last != 'U') {
            out_tol = last;
            num_part = tok.substr(0, tok.size() - 1);
        }

        size_t prefix_idx = std::string_view::npos;
        char prefix_char = '\0';
        for (size_t i = 0; i < num_part.size(); ++i) {
            char c = static_cast<char>(std::tolower(static_cast<unsigned char>(num_part[i])));
            if (c == 'r' || c == 'p' || c == 'n' || c == 'u' || c == 'm') {
                prefix_idx = i;
                prefix_char = c;
                break;
            }
        }

        if (prefix_idx != std::string_view::npos) {
            double multiplier = 1.0;
            if (prefix_char == 'r' || prefix_char == 'p') multiplier = 1.0;
            else if (prefix_char == 'n') multiplier = 1e3;
            else if (prefix_char == 'u') multiplier = 1e6;
            else if (prefix_char == 'm') multiplier = 1e9;

            std::string_view before = num_part.substr(0, prefix_idx);
            std::string_view after = num_part.substr(prefix_idx + 1);

            double v_before = 0.0, v_after = 0.0;
            if (!before.empty()) {
                if (auto [p, ec] = std::from_chars(before.data(), before.data() + before.size(), v_before); ec != std::errc()) {
                    return std::nullopt;
                }
            }
            double frac = 0.0;
            if (!after.empty()) {
                if (auto [p, ec] = std::from_chars(after.data(), after.data() + after.size(), v_after); ec == std::errc()) {
                    frac = v_after / std::pow(10.0, static_cast<double>(after.size()));
                }
            }
            return (v_before + frac) * multiplier;
        }

        bool all_digits = true;
        for (char c : num_part) {
            if (!std::isdigit(static_cast<unsigned char>(c))) { all_digits = false; break; }
        }

        if (all_digits) {
            if (num_part.size() == 3) {
                int d1 = num_part[0] - '0';
                int d2 = num_part[1] - '0';
                int d3 = num_part[2] - '0';
                int mantissa = d1 * 10 + d2;
                if (d3 <= 6) return mantissa * std::pow(10.0, d3);
                if (d3 == 8) return mantissa * 0.01;
                if (d3 == 9) return mantissa * 0.1;
                return std::nullopt;
            } else if (num_part.size() == 4) {
                int mantissa = (num_part[0] - '0') * 100 + (num_part[1] - '0') * 10 + (num_part[2] - '0');
                int exp = num_part[3] - '0';
                return mantissa * std::pow(10.0, exp);
            } else if (num_part.size() <= 2) {
                double val = 0.0;
                if (auto [p, ec] = std::from_chars(num_part.data(), num_part.data() + num_part.size(), val); ec == std::errc()) {
                    return val;
                }
            }
        }

        return std::nullopt;
    }

    static std::optional<ToleranceSpec> parse_tolerance(char code, double cap_pf) {
        char up = static_cast<char>(std::toupper(static_cast<unsigned char>(code)));
        ToleranceSpec tol;
        tol.code = up;

        if (cap_pf < 10.0) {
            tol.is_absolute = true;
            if (up == 'B') { tol.plus = tol.minus = 0.10; return tol; }
            if (up == 'C') { tol.plus = tol.minus = 0.25; return tol; }
            if (up == 'D') { tol.plus = tol.minus = 0.50; return tol; }
        }

        tol.is_absolute = false;
        switch (up) {
            case 'B': tol.plus = tol.minus = 0.1;  return tol;
            case 'C': tol.plus = tol.minus = 0.25; return tol;
            case 'D': tol.plus = tol.minus = 0.5;  return tol;
            case 'F': tol.plus = tol.minus = 1.0;  return tol;
            case 'G': tol.plus = tol.minus = 2.0;  return tol;
            case 'J': tol.plus = tol.minus = 5.0;  return tol;
            case 'K': tol.plus = tol.minus = 10.0; return tol;
            case 'M': tol.plus = tol.minus = 20.0; return tol;
            case 'Z': tol.plus = 80.0; tol.minus = 20.0; return tol;
            case 'P': tol.plus = 100.0; tol.minus = 0.0; return tol;
            default: return std::nullopt;
        }
    }

    static std::optional<double> parse_voltage(std::string_view tok) {
        if (tok.empty()) return std::nullopt;

        if (std::toupper(static_cast<unsigned char>(tok.back())) == 'V') {
            double v = 0.0;
            if (auto [p, ec] = std::from_chars(tok.data(), tok.data() + tok.size() - 1, v); ec == std::errc()) {
                return (v > 0.0) ? std::optional<double>{v} : std::nullopt;
            }
        }

        if (tok.size() == 2 && std::isdigit(static_cast<unsigned char>(tok[0]))) {
            int exp = tok[0] - '0';
            char base = static_cast<char>(std::toupper(static_cast<unsigned char>(tok[1])));
            double base_val = 0.0;
            switch (base) {
                case 'A': base_val = 1.0; break;
                case 'C': base_val = 1.6; break;
                case 'D': base_val = 2.0; break;
                case 'E': base_val = 2.5; break;
                case 'G': base_val = 4.0; break;
                case 'J': base_val = 6.3; break;
                case 'V': base_val = 3.5; break;
                case 'H': base_val = 5.0; break;
                default: return std::nullopt;
            }
            return base_val * std::pow(10.0, exp);
        }

        if (tok.size() == 1) {
            switch (tok[0]) {
                case 'e': return 2.5;
                case 'G': return 4.0;
                case 'J': return 6.3;
                case 'A': return 10.0;
                case 'C': return 16.0;
                case 'D': return 20.0;
                case 'E': return 25.0;
                case 'V': return 35.0;
                case 'H': return 50.0;
                default: return std::nullopt;
            }
        }

        return std::nullopt;
    }

    static std::optional<TempClassSpec> parse_temp_class(std::string_view tok) {
        std::string up;
        up.reserve(tok.size());
        for (char c : tok) up.push_back(static_cast<char>(std::toupper(static_cast<unsigned char>(c))));

        if (up == "C0G" || up == "NP0") {
            return TempClassSpec{"C0G/NP0", DielectricClass::ClassI, -55, 125, 0.54};
        }

        if (up.size() == 3) {
            int t_min = 0, t_max = 0;
            double drift = 0.0;

            if (up[0] == 'X') t_min = -55;
            else if (up[0] == 'Y') t_min = -30;
            else if (up[0] == 'Z') t_min = 10;
            else return std::nullopt;

            if (up[1] == '4') t_max = 65;
            else if (up[1] == '5') t_max = 85;
            else if (up[1] == '6') t_max = 105;
            else if (up[1] == '7') t_max = 125;
            else if (up[1] == '8') t_max = 150;
            else if (up[1] == '9') t_max = 200;
            else return std::nullopt;

            if (up[2] == 'P') drift = 10.0;
            else if (up[2] == 'R') drift = 15.0;
            else if (up[2] == 'S') drift = 22.0;
            else if (up[2] == 'U') drift = 56.0;
            else if (up[2] == 'V') drift = 82.0;
            else return std::nullopt;

            DielectricClass d = (drift > 22.0) ? DielectricClass::ClassIII : DielectricClass::ClassII;
            return TempClassSpec{up, d, t_min, t_max, drift};
        }

        return std::nullopt;
    }
};

} // namespace capdecoder

int main() {
    const std::vector<std::string_view> samples = {
        "104K 1H X7R",
        "2R2C 1H C0G",
        "475M 1C X5R",
        "4n7J 2A",
        "R47B 50V",
        "1002F 1E",
        "106 0J"
    };

    for (auto s : samples) {
        auto res = capdecoder::CapacitorParser::parse(s);
        if (res.has_value()) {
            std::cout << "Маркування: " << std::left << std::setw(14) << s 
                      << " -> Ємність: " << std::setw(10) << res->formatted_value 
                      << " (" << std::scientific << res->capacitance_farads << " F)\n";
            if (res->tolerance.has_value()) {
                if (res->tolerance->is_absolute) {
                    std::cout << "  Допуск: ±" << res->tolerance->plus << " pF (код " << res->tolerance->code << ")\n";
                } else {
                    std::cout << "  Допуск: +" << res->tolerance->plus << "% / -" << res->tolerance->minus << "% (код " << res->tolerance->code << ")\n";
                }
            }
            if (res->rated_voltage.has_value()) {
                std::cout << "  Напруга: " << std::fixed << std::setprecision(1) << *res->rated_voltage << " В (код " << res->voltage_code << ")\n";
            }
            if (res->temp_class.has_value()) {
                std::cout << "  Клас: " << res->temp_class->code << " (" << res->temp_class->min_celsius << "°C...+" << res->temp_class->max_celsius << "°C, max ΔC = ±" << res->temp_class->max_drift_pct << "%)\n";
            }
            std::cout << "  E24-валідація: найближчий " << res->nearest_e24_nominal << " pF (похибка " 
                      << std::fixed << std::setprecision(2) << res->e24_error_pct << "%)\n";
            std::cout << "----------------------------------------------------------------\n";
        }
    }
    return 0;
}
