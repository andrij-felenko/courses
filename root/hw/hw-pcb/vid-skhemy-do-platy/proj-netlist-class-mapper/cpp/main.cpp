#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <format>
#include <algorithm>
#include <cctype>
#include <span>

namespace eda::mapper {

enum class NetClassId {
    Default,
    Power,
    HighSpeed,
    Analog,
    RF
};

[[nodiscard]] constexpr std::string_view to_string(NetClassId id) noexcept {
    switch (id) {
        case NetClassId::Power:     return "Power";
        case NetClassId::HighSpeed: return "HighSpeed";
        case NetClassId::Analog:    return "Analog";
        case NetClassId::RF:        return "RF";
        default:                    return "Default";
    }
}

struct PinNode {
    std::string refdes;
    std::string pin_number;
    std::string pin_type;
};

struct NetRecord {
    std::string name;
    int code{0};
    std::vector<PinNode> pins;
    NetClassId assigned_class{NetClassId::Default};
    double track_width_mm{0.20};
    double clearance_mm{0.20};
    double via_drill_mm{0.30};
    double via_pad_mm{0.60};
};

struct MappingRule {
    std::string pattern;
    NetClassId target_class{NetClassId::Default};
    int priority{0};
    double track_width_mm{0.20};
    double clearance_mm{0.20};
    double via_drill_mm{0.30};
    double via_pad_mm{0.60};

    [[nodiscard]] bool matches(std::string_view net_name) const noexcept {
        if (pattern == "*") return true;
        if (pattern.ends_with('*')) {
            std::string_view prefix = std::string_view(pattern).substr(0, pattern.size() - 1);
            return net_name.starts_with(prefix);
        }
        if (pattern.starts_with('*')) {
            std::string_view suffix = std::string_view(pattern).substr(1);
            return net_name.ends_with(suffix);
        }
        return net_name == pattern;
    }
};

class NetlistClassifierEngine {
public:
    void add_rule(std::string_view pattern, NetClassId cls, int priority,
                  double width, double clearance, double via_drill, double via_pad) {
        rules_.push_back(MappingRule{
            std::string(pattern), cls, priority, width, clearance, via_drill, via_pad
        });
    }

    void parse_and_process(std::string_view s_expression_text) {
        std::size_t cursor = 0;
        while (cursor < s_expression_text.size()) {
            cursor = skip_whitespace(s_expression_text, cursor);
            if (cursor >= s_expression_text.size()) break;

            if (s_expression_text[cursor] == '(') {
                cursor++;
                auto tag = read_token(s_expression_text, cursor);
                if (tag == "net") {
                    parse_net_entry(s_expression_text, cursor);
                }
            } else {
                cursor++;
            }
        }
        apply_classification_rules();
    }

    void emit_audit_report() const {
        std::cout << "\n" << std::string(88, '=') << "\n";
        std::cout << "                  PCB NETLIST CLASSIFICATION & DESIGN RULE REPORT (C++20)\n";
        std::cout << std::string(88, '=') << "\n";
        std::cout << std::format("{:<24} | {:<12} | {:<8} | {:<10} | {:<12} | {:<6}\n",
                                 "Net Identifier", "Class", "Width", "Clearance", "Via (D/P)", "Nodes");
        std::cout << std::string(88, '-') << "\n";

        for (const auto& net : nets_) {
            std::string via_fmt = std::format("{:.2f}/{:.2f}", net.via_drill_mm, net.via_pad_mm);
            std::cout << std::format("{:<24} | {:<12} | {:>5.2f} mm | {:>6.2f} mm | {:<12} | {:>4}\n",
                                     net.name, to_string(net.assigned_class),
                                     net.track_width_mm, net.clearance_mm, via_fmt, net.pins.size());
        }
        std::cout << std::string(88, '=') << "\n";
        std::cout << std::format("Total electrical nets parsed: {}\n\n", nets_.size());
    }

    [[nodiscard]] std::span<const NetRecord> nets() const noexcept {
        return nets_;
    }

private:
    std::vector<MappingRule> rules_;
    std::vector<NetRecord> nets_;

    static std::size_t skip_whitespace(std::string_view s, std::size_t pos) noexcept {
        while (pos < s.size()) {
            if (std::isspace(static_cast<unsigned char>(s[pos])) || s[pos] == '\r' || s[pos] == '\n') {
                pos++;
            } else if (s[pos] == ';') {
                while (pos < s.size() && s[pos] != '\n') pos++;
            } else {
                break;
            }
        }
        return pos;
    }

    static std::string_view read_token(std::string_view s, std::size_t& pos) noexcept {
        pos = skip_whitespace(s, pos);
        if (pos >= s.size()) return {};

        std::size_t start = pos;
        if (s[pos] == '"') {
            start = ++pos;
            while (pos < s.size() && s[pos] != '"') pos++;
            std::string_view token = s.substr(start, pos - start);
            if (pos < s.size() && s[pos] == '"') pos++;
            return token;
        }

        while (pos < s.size() && !std::isspace(static_cast<unsigned char>(s[pos])) && s[pos] != '(' && s[pos] != ')') {
            pos++;
        }
        return s.substr(start, pos - start);
    }

    static void consume_closing_paren(std::string_view s, std::size_t& pos) noexcept {
        int depth = 1;
        while (pos < s.size() && depth > 0) {
            if (s[pos] == '(') depth++;
            else if (s[pos] == ')') depth--;
            pos++;
        }
    }

    void parse_net_entry(std::string_view s, std::size_t& pos) {
        NetRecord net;
        net.code = static_cast<int>(nets_.size() + 1);

        while (pos < s.size() && s[pos] != ')') {
            pos = skip_whitespace(s, pos);
            if (pos < s.size() && s[pos] == '(') {
                pos++;
                auto key = read_token(s, pos);
                if (key == "name") {
                    net.name = std::string(read_token(s, pos));
                    consume_closing_paren(s, pos);
                } else if (key == "node") {
                    parse_node_entry(s, pos, net);
                } else {
                    consume_closing_paren(s, pos);
                }
            } else if (pos < s.size() && s[pos] == ')') {
                pos++;
                break;
            } else {
                pos++;
            }
        }
        if (!net.name.empty()) {
            nets_.push_back(std::move(net));
        }
    }

    static void parse_node_entry(std::string_view s, std::size_t& pos, NetRecord& net) {
        PinNode pin;
        while (pos < s.size() && s[pos] != ')') {
            pos = skip_whitespace(s, pos);
            if (pos < s.size() && s[pos] == '(') {
                pos++;
                auto attr = read_token(s, pos);
                if (attr == "ref") {
                    pin.refdes = std::string(read_token(s, pos));
                } else if (attr == "pin") {
                    pin.pin_number = std::string(read_token(s, pos));
                } else if (attr == "pintype") {
                    pin.pin_type = std::string(read_token(s, pos));
                }
                consume_closing_paren(s, pos);
            } else if (pos < s.size() && s[pos] == ')') {
                pos++;
                break;
            } else {
                pos++;
            }
        }
        if (!pin.refdes.empty()) {
            net.pins.push_back(std::move(pin));
        }
    }

    void apply_classification_rules() {
        for (auto& net : nets_) {
            net.assigned_class = NetClassId::Default;
            net.track_width_mm = 0.20;
            net.clearance_mm = 0.20;
            net.via_drill_mm = 0.30;
            net.via_pad_mm = 0.60;

            int best_priority = -1;
            for (const auto& rule : rules_) {
                if (rule.matches(net.name) && rule.priority > best_priority) {
                    best_priority = rule.priority;
                    net.assigned_class = rule.target_class;
                    net.track_width_mm = rule.track_width_mm;
                    net.clearance_mm = rule.clearance_mm;
                    net.via_drill_mm = rule.via_drill_mm;
                    net.via_pad_mm = rule.via_pad_mm;
                }
            }
        }
    }
};

} // namespace eda::mapper
