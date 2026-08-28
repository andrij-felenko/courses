#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <unordered_map>
#include <format>
#include <algorithm>

enum class Severity {
    Info,
    Warning,
    Error
};

enum class PinType {
    Input,
    Output,
    OpenDrain,
    PowerIn,
    PowerOut,
    Passive
};

struct Pin {
    std::string name;
    PinType type;
    size_t parent_component_idx;
    size_t net_idx;
};

struct Component {
    std::string refdes;
    std::string value_raw;
    std::optional<double> voltage_rating;
    bool is_dnp{false};
    std::vector<size_t> pin_indices;
};

struct Net {
    std::string name;
    double operating_voltage{0.0};
    bool is_power_rail{false};
    std::vector<size_t> pin_indices;
};

struct Junction {
    double x{0.0};
    double y{0.0};
    int connected_wires{0};
    std::string sheet_name;
};

struct Issue {
    Severity severity;
    std::string rule_code;
    std::string message;
};

class SchematicLinter {
public:
    size_t add_net(std::string name, double op_voltage = 0.0, bool is_pwr = false) {
        nets_.push_back(Net{
            .name = std::move(name),
            .operating_voltage = op_voltage,
            .is_power_rail = is_pwr,
            .pin_indices = {}
        });
        return nets_.size() - 1;
    }

    size_t add_component(std::string refdes, std::string val, std::optional<double> volt_rating = std::nullopt) {
        components_.push_back(Component{
            .refdes = std::move(refdes),
            .value_raw = std::move(val),
            .voltage_rating = volt_rating,
            .is_dnp = false,
            .pin_indices = {}
        });
        return components_.size() - 1;
    }

    void connect_pin(size_t comp_idx, std::string pin_name, PinType type, size_t net_idx) {
        if (comp_idx >= components_.size() || net_idx >= nets_.size()) return;

        const size_t pin_idx = pins_.size();
        pins_.push_back(Pin{
            .name = std::move(pin_name),
            .type = type,
            .parent_component_idx = comp_idx,
            .net_idx = net_idx
        });

        components_[comp_idx].pin_indices.push_back(pin_idx);
        nets_[net_idx].pin_indices.push_back(pin_idx);
    }

    void add_junction(double x, double y, int wires, std::string sheet) {
        junctions_.push_back(Junction{
            .x = x,
            .y = y,
            .connected_wires = wires,
            .sheet_name = std::move(sheet)
        });
    }

    void run_checks() {
        issues_.clear();
        check_4way_junctions();
        check_net_drivers();
        check_component_hygiene();
    }

    void print_report() const {
        std::cout << "====================================================================\n";
        std::cout << "                 ЗВІТ СХЕМНОГО ЛІНТЕРА (C++20)                      \n";
        std::cout << "====================================================================\n";
        std::cout << std::format("Проаналізовано: {} компонентів, {} ланцюгів, {} вузлів.\n\n",
                                 components_.size(), nets_.size(), junctions_.size());

        if (issues_.empty()) {
            std::cout << "[OK] Усі правила гігієни виконано успішно.\n";
            return;
        }

        for (const auto &iss : issues_) {
            std::string_view sev_str = "INFO";
            if (iss.severity == Severity::Warning) sev_str = "ПОПЕРЕДЖЕННЯ";
            else if (iss.severity == Severity::Error) sev_str = "ПОМИЛКА";

            std::cout << std::format("[{}] [{}] {}\n", sev_str, iss.rule_code, iss.message);
        }
        std::cout << "====================================================================\n";
        std::cout << std::format("Разом зафіксовано зауважень: {}\n", issues_.size());
    }

    [[nodiscard]] const std::vector<Issue>& issues() const noexcept { return issues_; }

private:
    void add_issue(Severity sev, std::string code, std::string msg) {
        issues_.push_back(Issue{.severity = sev, .rule_code = std::move(code), .message = std::move(msg)});
    }

    void check_4way_junctions() {
        for (const auto &j : junctions_) {
            if (j.connected_wires >= 4) {
                add_issue(Severity::Error, "HYG-01-4WAY",
                    std::format("4-сторонній вузол на аркуші '{}' (X={:.1f}, Y={:.1f}). Замініть на зміщені Т-вузли!",
                                j.sheet_name, j.x, j.y));
            }
        }
    }

    void check_net_drivers() {
        for (const auto &net : nets_) {
            int out_drivers = 0;
            int od_drivers = 0;
            int inputs = 0;
            int passives = 0;

            for (size_t p_idx : net.pin_indices) {
                switch (pins_[p_idx].type) {
                    case PinType::Output:
                    case PinType::PowerOut:
                        out_drivers++;
                        break;
                    case PinType::OpenDrain:
                        od_drivers++;
                        break;
                    case PinType::Input:
                    case PinType::PowerIn:
                        inputs++;
                        break;
                    case PinType::Passive:
                        passives++;
                        break;
                }
            }

            // Колізія виходів
            if (out_drivers > 1) {
                add_issue(Severity::Error, "ERC-02-COLLISION",
                    std::format("Ланцюг '{}' має {} активних виходів Output. Коротке замикання драйверів!",
                                net.name, out_drivers));
            }

            // Плаваючий вхід
            if (inputs > 0 && out_drivers == 0 && od_drivers == 0 && passives == 0 && !net.is_power_rail) {
                add_issue(Severity::Warning, "ERC-03-FLOATING",
                    std::format("Ланцюг '{}' має {} входів без джерела сигналу або резистора підтяжки.",
                                net.name, inputs));
            }

            // Поодинока мітка
            if (net.pin_indices.size() == 1 && !net.is_power_rail) {
                add_issue(Severity::Warning, "HYG-04-SINGLEPIN",
                    std::format("Ланцюг '{}' має лише одне підключення. Перевірте наявність одруківок у мітці!",
                                net.name));
            }
        }
    }

    void check_component_hygiene() {
        for (const auto &comp : components_) {
            if (comp.is_dnp) continue;

            // Перевірка конденсаторів
            if (!comp.refdes.empty() && comp.refdes[0] == 'C') {
                for (size_t p_idx : comp.pin_indices) {
                    const auto &net = nets_[pins_[p_idx].net_idx];
                    if (net.is_power_rail && net.operating_voltage > 0.0) {
                        if (!comp.voltage_rating.has_value() || *comp.voltage_rating <= 0.0) {
                            add_issue(Severity::Error, "HYG-05-NOVOLD",
                                std::format("Конденсатор {} ({}) на шині {:.1f}V не має робочої напруги!",
                                            comp.refdes, comp.value_raw, net.operating_voltage));
                        } else if (*comp.voltage_rating < net.operating_voltage * 1.5) {
                            add_issue(Severity::Warning, "HYG-06-DERATING",
                                std::format("Конденсатор {} ({:.0f}V) на шині {:.1f}V має недостатній запас (<1.5x). Ризик DC-bias деградації!",
                                            comp.refdes, *comp.voltage_rating, net.operating_voltage));
                        }
                    }
                }
            }

            // Перевірка крапки у номіналі
            if (comp.value_raw.find('.') != std::string::npos) {
                add_issue(Severity::Info, "HYG-07-DOTVALUE",
                    std::format("Компонент {}: Номінал '{}' містить крапку замість синтаксису R-S-H.",
                                comp.refdes, comp.value_raw));
            }
        }
    }

    std::vector<Component> components_;
    std::vector<Pin> pins_;
    std::vector<Net> nets_;
    std::vector<Junction> junctions_;
    std::vector<Issue> issues_;
};

int main() {
    SchematicLinter linter;

    const auto vcc12 = linter.add_net("+12V", 12.0, true);
    const auto gnd   = linter.add_net("GND", 0.0, true);
    const auto miso  = linter.add_net("SPI_MISO", 3.3, false);
    const auto alert = linter.add_net("IRQ_ALERT", 3.3, false);
    const auto typo  = linter.add_net("SENSOR_DAT0", 3.3, false);

    const auto c1 = linter.add_component("C101", "10u", 16.0); // 16V на 12V -> Derating warning
    linter.connect_pin(c1, "1", PinType::Passive, vcc12);
    linter.connect_pin(c1, "2", PinType::Passive, gnd);

    const auto r1 = linter.add_component("R101", "4.7k"); // Крапка -> Info warning
    linter.connect_pin(r1, "1", PinType::Passive, vcc12);
    linter.connect_pin(r1, "2", PinType::Passive, miso);

    const auto u1 = linter.add_component("U1", "STM32F4");
    linter.connect_pin(u1, "PA6", PinType::Output, miso);
    linter.connect_pin(u1, "PB0", PinType::Input, alert); // Плаваючий вхід

    const auto u2 = linter.add_component("U2", "ADC_DRIVER");
    linter.connect_pin(u2, "SDO", PinType::Output, miso); // Колізія виходів на MISO
    linter.connect_pin(u2, "DATA", PinType::Output, typo); // Single-pin net

    linter.add_junction(125.0, 80.0, 4, "Power_Sheet.kicad_sch"); // 4-way перехрестя

    linter.run_checks();
    linter.print_report();

    return 0;
}
