#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <numbers>
#include <memory>
#include <iomanip>
#include <span>

namespace eco {

enum class WireGauge : uint8_t {
    AWG30 = 0,
    AWG32,
    AWG34,
    AWG36,
    AWG38,
    Count
};

struct WireSpec {
    WireGauge gauge;
    std::string_view name;
    double diameter_mm;
    double max_current_a;
    double r_per_meter;
};

constexpr WireSpec WIRE_TABLE[] = {
    {WireGauge::AWG30, "AWG 30 (0.25mm Kynar)", 0.254, 0.85, 0.338},
    {WireGauge::AWG32, "AWG 32 (0.20mm PTFE)",  0.203, 0.55, 0.531},
    {WireGauge::AWG34, "AWG 34 (0.16mm Enamel)",0.160, 0.35, 0.855},
    {WireGauge::AWG36, "AWG 36 (0.12mm Enamel)",0.127, 0.20, 1.360},
    {WireGauge::AWG38, "AWG 38 (0.10mm Enamel)",0.101, 0.12, 2.130}
};

enum class StepType : uint8_t {
    Cut,
    Jumper,
    PinLift,
    CompAdd
};

enum class SignalDomain : uint8_t {
    Power,
    SlowDigital,
    FastDigital,
    Analog
};

struct EcoStep {
    StepType type;
    std::string id;
    std::string net_name;
    SignalDomain domain{SignalDomain::SlowDigital};
    std::string loc_from;
    std::string loc_to;
    WireGauge wire{WireGauge::AWG34};
    double length_mm{0.0};
    double height_above_gnd_mm{0.3};
    double current_ma{0.0};
    double nominal_voltage_v{3.3};
    std::string comp_val;
    std::string notes;
};

struct ValidationReport {
    int errors{0};
    int warnings{0};
    std::vector<double> total_wire_len_mm{std::vector<double>(static_cast<size_t>(WireGauge::Count), 0.0)};
    int total_cuts{0};
    int total_jumpers{0};
    int total_pin_lifts{0};
    int total_comps{0};
};

class EcoProject {
public:
    EcoProject(std::string name, std::string rev_from, std::string rev_to)
        : name_(std::move(name)), rev_from_(std::move(rev_from)), rev_to_(std::move(rev_to)) {}

    void add_cut(std::string id, std::string net, std::string loc, std::string notes) {
        steps_.push_back(EcoStep{
            .type = StepType::Cut,
            .id = std::move(id),
            .net_name = std::move(net),
            .loc_from = std::move(loc),
            .notes = std::move(notes)
        });
    }

    void add_jumper(std::string id, std::string net, SignalDomain domain,
                    std::string from, std::string to, WireGauge wire,
                    double len_mm, double h_gnd_mm, double current_ma, double v_nom, std::string notes) {
        steps_.push_back(EcoStep{
            .type = StepType::Jumper,
            .id = std::move(id),
            .net_name = std::move(net),
            .domain = domain,
            .loc_from = std::move(from),
            .loc_to = std::move(to),
            .wire = wire,
            .length_mm = len_mm,
            .height_above_gnd_mm = h_gnd_mm,
            .current_ma = current_ma,
            .nominal_voltage_v = v_nom,
            .notes = std::move(notes)
        });
    }

    void add_pin_lift(std::string id, std::string net, std::string ic_pin, std::string notes) {
        steps_.push_back(EcoStep{
            .type = StepType::PinLift,
            .id = std::move(id),
            .net_name = std::move(net),
            .loc_from = std::move(ic_pin),
            .notes = std::move(notes)
        });
    }

    void add_component(std::string id, std::string net, std::string val,
                       std::string from, std::string to, std::string notes) {
        steps_.push_back(EcoStep{
            .type = StepType::CompAdd,
            .id = std::move(id),
            .net_name = std::move(net),
            .loc_from = std::move(from),
            .loc_to = std::move(to),
            .comp_val = std::move(val),
            .notes = std::move(notes)
        });
    }

    [[nodiscard]] static constexpr double calc_loop_inductance_nh(double len_mm, double dia_mm, double h_gnd_mm) noexcept {
        if (dia_mm <= 0.0 || h_gnd_mm <= 0.0 || len_mm <= 0.0) return 0.0;
        double ratio = (4.0 * h_gnd_mm) / dia_mm;
        if (ratio <= 1.0) ratio = 1.05;
        double l_per_m = 2.0e-7 * std::log(ratio);
        return (l_per_m * (len_mm / 1000.0)) * 1.0e9;
    }

    [[nodiscard]] ValidationReport validate() const {
        ValidationReport rep;
        for (const auto &s : steps_) {
            switch (s.type) {
                case StepType::Cut:
                    rep.total_cuts++;
                    break;
                case StepType::PinLift:
                    rep.total_pin_lifts++;
                    break;
                case StepType::CompAdd:
                    rep.total_comps++;
                    break;
                case StepType::Jumper: {
                    rep.total_jumpers++;
                    const auto idx = static_cast<size_t>(s.wire);
                    if (idx < WIRE_TABLE.size()) {
                        rep.total_wire_len_mm[idx] += s.length_mm;
                        const auto &ws = WIRE_TABLE[idx];
                        const double current_a = s.current_ma / 1000.0;

                        if (current_a > ws.max_current_a) {
                            rep.errors++;
                            std::cout << "[ERROR] " << s.id << ": Струм " << current_a << "A перевищує ліміт "
                                      << ws.max_current_a << "A для " << ws.name << "!\n";
                        }

                        if (s.nominal_voltage_v > 0.0) {
                            const double r_total = ws.r_per_meter * (s.length_mm / 1000.0);
                            const double v_drop = current_a * r_total;
                            const double drop_pct = (v_drop / s.nominal_voltage_v) * 100.0;
                            if (drop_pct > 2.0) {
                                rep.warnings++;
                                std::cout << "[WARN] " << s.id << ": Падіння напруги " << std::fixed
                                          << std::setprecision(1) << drop_pct << "% (" << v_drop
                                          << "V) на сітці " << s.net_name << " > 2.0%\n";
                            }
                        }

                        if (s.domain == SignalDomain::FastDigital && s.height_above_gnd_mm > 1.0) {
                            const double l_nh = calc_loop_inductance_nh(s.length_mm, ws.diameter_mm, s.height_above_gnd_mm);
                            rep.warnings++;
                            std::cout << "[WARN] " << s.id << ": Швидкісна сітка " << s.net_name
                                      << " має високу індуктивність " << std::fixed << std::setprecision(1)
                                      << l_nh << "nH (h=" << s.height_above_gnd_mm << "mm)!\n";
                        }
                    }
                    break;
                }
            }
        }
        return rep;
    }

    void print_runsheet(const ValidationReport &rep) const {
        std::cout << "\n# Технологічна карта доопрацювання ECO: " << name_ << "\n";
        std::cout << "**Перехід ревізій:** " << rev_from_ << " -> " << rev_to_ << "\n\n";

        std::cout << "## 1. Специфікація матеріалів модифікації (BOM)\n\n";
        std::cout << "| Матеріал / Калібр | Загальна довжина / Кількість | Призначення |\n";
        std::cout << "|---|---|---|\n";
        for (size_t w = 0; w < WIRE_TABLE.size(); ++w) {
            if (rep.total_wire_len_mm[w] > 0.0) {
                std::cout << "| " << WIRE_TABLE[w].name << " | " << std::fixed << std::setprecision(1)
                          << rep.total_wire_len_mm[w] << " мм (" << (rep.total_wire_len_mm[w] / 10.0)
                          << " см) | Монтажні перемички |\n";
            }
        }
        std::cout << "| УФ-маска рідка | " << (rep.total_cuts + rep.total_jumpers * 2)
                  << " точок герметизації | Захист різів і фіксація |\n";
        std::cout << "| Каптоновий скотч | За потребою | Тимчасове утримання трас |\n\n";

        std::cout << "## 2. Покрокова інструкція монтажника (Rework Run-Sheet)\n\n";
        std::cout << "| Крок | Дія | Локація / Від | Куди | Параметри / Провід | Примітки |\n";
        std::cout << "|---|---|---|---|---|---|\n";

        for (const auto &s : steps_) {
            switch (s.type) {
                case StepType::Cut:
                    std::cout << "| " << s.id << " | **CUT (Різ)** | " << s.loc_from
                              << " | — | IPC-7721 V-Cut 1.0mm | " << s.notes << " |\n";
                    break;
                case StepType::PinLift:
                    std::cout << "| " << s.id << " | **PIN LIFT** | " << s.loc_from
                              << " | — | Відгин ніжки 30° | " << s.notes << " |\n";
                    break;
                case StepType::CompAdd:
                    std::cout << "| " << s.id << " | **COMP ADD** | " << s.loc_from
                              << " | " << s.loc_to << " | " << s.comp_val << " (Tombstone) | " << s.notes << " |\n";
                    break;
                case StepType::Jumper: {
                    const auto &ws = WIRE_TABLE[static_cast<size_t>(s.wire)];
                    std::cout << "| " << s.id << " | **JUMPER** | " << s.loc_from
                              << " | " << s.loc_to << " | " << ws.name << ", L=" << std::fixed << std::setprecision(0)
                              << s.length_mm << "мм | " << s.notes << " |\n";
                    break;
                }
            }
        }

        std::cout << "\n## 3. Чекліст контролю та верифікації ВТК\n\n";
        for (const auto &s : steps_) {
            if (s.type == StepType::Cut) {
                std::cout << "- [ ] **" << s.id << "**: Перевірити опір ізоляції розрізу на "
                          << s.loc_from << " (R > 10 МОм, КЗ на GND відсутнє).\n";
            } else if (s.type == StepType::Jumper) {
                std::cout << "- [ ] **" << s.id << "**: Продзвонити ланцюг " << s.net_name
                          << " (" << s.loc_from << " -> " << s.loc_to << "), R < 0.5 Ом, фіксація УФ-маскою.\n";
            } else if (s.type == StepType::CompAdd) {
                std::cout << "- [ ] **" << s.id << "**: Контроль номіналу " << s.comp_val
                          << " між " << s.loc_from << " та " << s.loc_to << " під мікроскопом.\n";
            }
        }
    }

private:
    std::string name_;
    std::string rev_from_;
    std::string rev_to_;
    std::vector<EcoStep> steps_;
};

} // namespace eco

int main() {
    eco::EcoProject proj("IoT Sensor Hub Telemetry Node", "Rev A", "Rev A.1");

    proj.add_cut("CUT-01", "UART1_TX", "U3.Pin4 (L1 Trace near R12)", "Подвійний V-кут, розрив TX");
    proj.add_cut("CUT-02", "UART1_RX", "U3.Pin5 (L1 Trace near R13)", "Подвійний V-кут, розрив RX");
    proj.add_pin_lift("LIFT-01", "MCU_NRST", "U1.Pin7 (NRST)", "Підняти вивід для додавання підтяжки");

    proj.add_component("ADD-R1", "MCU_NRST_PU", "10k 0402", "U1.Pin7", "C12.Pad1 (3.3V)", "Підтягуючий резистор");

    proj.add_jumper("JUMP-01", "UART1_SWAP_TX", eco::SignalDomain::SlowDigital,
                    "U3.Pin4", "U1.Pin12 (MCU_RX)", eco::WireGauge::AWG34, 35.0, 0.3, 15.0, 3.3, "Фіксація до плати маскою");
    proj.add_jumper("JUMP-02", "UART1_SWAP_RX", eco::SignalDomain::SlowDigital,
                    "U3.Pin5", "U1.Pin11 (MCU_TX)", eco::WireGauge::AWG34, 35.0, 0.3, 15.0, 3.3, "Фіксація до плати маскою");
    proj.add_jumper("JUMP-03", "VCC_RADIO_3V3", eco::SignalDomain::Power,
                    "C5.Pad1 (+3.3V)", "U8.Pin1 (VCC_RF)", eco::WireGauge::AWG30, 80.0, 0.2, 450.0, 3.3, "Силове живлення RF");
    proj.add_jumper("JUMP-04", "SPI_CLK_FAST", eco::SignalDomain::FastDigital,
                    "U1.Pin24", "U4.Pin6", eco::WireGauge::AWG36, 45.0, 8.0, 20.0, 3.3, "Помилка монтажу: піднятий у повітря");

    std::cout << "=== ВАЛІДАЦІЯ ТА РОЗРАХУНОК ECO (C++20) ===\n";
    const auto rep = proj.validate();
    std::cout << "Валідацію завершено: помилок = " << rep.errors << ", попереджень = " << rep.warnings << "\n";

    proj.print_runsheet(rep);
    return 0;
}
