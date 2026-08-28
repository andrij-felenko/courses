#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <format>
#include <cmath>
#include <algorithm>
#include <memory>
#include <numeric>

namespace dft::core {

enum class NetClass {
    Power,
    Reset,
    Clock,
    Analog,
    HighSpeed,
    General
};

enum class ProbeTipType {
    Crown4Point,
    Spear30Deg,
    Serrated,
    ConcaveCup
};

struct NetRecord {
    std::string name;
    NetClass net_class{NetClass::General};
    bool has_testpoint{false};
    size_t tp_index{0};
    float weight{1.0f};
    uint32_t pin_count{0};
};

struct TestPointRecord {
    std::string net_name;
    std::string label;
    float x_mm{0.0f};
    float y_mm{0.0f};
    float diameter_mm{1.0f};
    bool on_bottom_layer{true};
    ProbeTipType recommended_tip{ProbeTipType::Crown4Point};
    float stub_length_mm{0.0f};
    bool has_clearance_violation{false};
};

struct ComponentRecord {
    std::string ref_des;
    float x_mm{0.0f};
    float y_mm{0.0f};
    float width_mm{0.0f};
    float height_mm{0.0f};
    float z_height_mm{1.0f};
    bool on_bottom_layer{false};
};

struct DftAuditReport {
    size_t total_nets{0};
    size_t covered_nets{0};
    size_t power_nets_total{0};
    size_t power_nets_covered{0};
    size_t reset_nets_total{0};
    size_t reset_nets_covered{0};
    size_t analog_nets_total{0};
    size_t analog_nets_covered{0};
    size_t clock_nets_total{0};
    size_t clock_nets_covered{0};
    size_t high_speed_nets_total{0};
    size_t high_speed_stubs_flagged{0};
    size_t clearance_violations{0};
    size_t layer_violations{0};
    float dft_weighted_score{0.0f};
    float total_probe_force_newtons{0.0f};
    float center_of_force_x_mm{0.0f};
    float center_of_force_y_mm{0.0f};
};

class DftAnalyzerEngine {
public:
    [[nodiscard]] static NetClass classify_net(std::string_view name) noexcept {
        if (name.contains("VCC") || name.contains("VDD") || name.contains("GND") ||
            name.contains("+3V3") || name.contains("+5V") || name.contains("+12V") ||
            name.contains("+1V8") || name.contains("+1V2") || name.contains("VBAT") ||
            name.contains("VBUS") || name.contains("AGND") || name.contains("DGND")) {
            return NetClass::Power;
        }
        if (name.contains("RESET") || name.contains("NRST") || name.contains("RST_N") || name.contains("POR")) {
            return NetClass::Reset;
        }
        if (name.contains("CLK") || name.contains("OSC") || name.contains("MCLK") || name.contains("TCK")) {
            return NetClass::Clock;
        }
        if (name.contains("ADC") || name.contains("SENSE") || name.contains("VREF") || name.contains("ANALOG")) {
            return NetClass::Analog;
        }
        if (name.contains("USB") || name.contains("ETH") || name.contains("DDR") ||
            name.contains("PCIE") || name.contains("MIPI") || name.contains("SGMII")) {
            return NetClass::HighSpeed;
        }
        return NetClass::General;
    }

    [[nodiscard]] static constexpr float get_weight(NetClass nc) noexcept {
        switch (nc) {
            case NetClass::Power:     return 10.0f;
            case NetClass::Reset:     return 8.0f;
            case NetClass::Analog:    return 6.0f;
            case NetClass::Clock:     return 5.0f;
            case NetClass::HighSpeed: return 2.0f;
            default:                  return 1.0f;
        }
    }

    [[nodiscard]] static std::string_view tip_to_string(ProbeTipType pt) noexcept {
        switch (pt) {
            case ProbeTipType::Crown4Point: return "Crown-4pt (100mil/2.0N)";
            case ProbeTipType::Spear30Deg:  return "Spear-30deg (75mil/2.5N)";
            case ProbeTipType::Serrated:    return "Serrated (100mil/2.0N)";
            case ProbeTipType::ConcaveCup:  return "Concave-Cup (100mil/1.5N)";
            default:                        return "Standard-Crown";
        }
    }

    [[nodiscard]] static float distance(float x1, float y1, float x2, float y2) noexcept {
        return std::hypot(x1 - x2, y1 - y2);
    }

    [[nodiscard]] DftAuditReport execute_audit(std::vector<NetRecord>& nets,
                                               std::vector<TestPointRecord>& tps,
                                               const std::vector<ComponentRecord>& comps) const {
        DftAuditReport report;
        report.total_nets = nets.size();

        float sum_weighted_covered = 0.0f;
        float sum_weighted_total = 0.0f;
        float sum_force_x = 0.0f;
        float sum_force_y = 0.0f;

        // [1] Аудит покриття ланцюгів
        for (auto& net : nets) {
            net.net_class = classify_net(net.name);
            net.weight = get_weight(net.net_class);
            net.has_testpoint = false;

            sum_weighted_total += net.weight;

            switch (net.net_class) {
                case NetClass::Power:     report.power_nets_total++; break;
                case NetClass::Reset:     report.reset_nets_total++; break;
                case NetClass::Analog:    report.analog_nets_total++; break;
                case NetClass::Clock:     report.clock_nets_total++; break;
                case NetClass::HighSpeed: report.high_speed_nets_total++; break;
                default: break;
            }

            for (size_t j = 0; j < tps.size(); ++j) {
                if (net.name == tps[j].net_name) {
                    net.has_testpoint = true;
                    net.tp_index = j;
                    break;
                }
            }

            if (net.has_testpoint) {
                report.covered_nets++;
                sum_weighted_covered += net.weight;

                switch (net.net_class) {
                    case NetClass::Power:  report.power_nets_covered++; break;
                    case NetClass::Reset:  report.reset_nets_covered++; break;
                    case NetClass::Analog: report.analog_nets_covered++; break;
                    case NetClass::Clock:  report.clock_nets_covered++; break;
                    default: break;
                }
            }
        }

        if (sum_weighted_total > 0.0f) {
            report.dft_weighted_score = (sum_weighted_covered / sum_weighted_total) * 100.0f;
        }

        // [2] Фізичні зазори та вибір зондів
        for (size_t i = 0; i < tps.size(); ++i) {
            tps[i].has_clearance_violation = false;

            if (!tps[i].on_bottom_layer) {
                report.layer_violations++;
            }

            if (tps[i].diameter_mm >= 1.0f) {
                tps[i].recommended_tip = ProbeTipType::Crown4Point;
            } else if (tps[i].diameter_mm >= 0.75f) {
                tps[i].recommended_tip = ProbeTipType::Spear30Deg;
            } else {
                tps[i].recommended_tip = ProbeTipType::Serrated;
            }

            const auto nc = classify_net(tps[i].net_name);
            if (nc == NetClass::HighSpeed && tps[i].stub_length_mm > 2.5f) {
                report.high_speed_stubs_flagged++;
            }

            for (size_t j = i + 1; j < tps.size(); ++j) {
                const float d = distance(tps[i].x_mm, tps[i].y_mm, tps[j].x_mm, tps[j].y_mm);
                if (d < 1.27f) {
                    report.clearance_violations++;
                    tps[i].has_clearance_violation = true;
                    tps[j].has_clearance_violation = true;
                }
            }

            for (const auto& comp : comps) {
                if (comp.on_bottom_layer != tps[i].on_bottom_layer) {
                    continue;
                }
                const float dc = distance(tps[i].x_mm, tps[i].y_mm, comp.x_mm, comp.y_mm);
                const float min_req = (comp.z_height_mm >= 4.0f) ? 3.5f : 1.27f;
                if (dc < min_req) {
                    report.clearance_violations++;
                    tps[i].has_clearance_violation = true;
                }
            }

            constexpr float PIN_FORCE_N = 2.0f;
            sum_force_x += tps[i].x_mm * PIN_FORCE_N;
            sum_force_y += tps[i].y_mm * PIN_FORCE_N;
        }

        report.total_probe_force_newtons = static_cast<float>(tps.size()) * 2.0f;
        if (!tps.empty()) {
            report.center_of_force_x_mm = sum_force_x / report.total_probe_force_newtons;
            report.center_of_force_y_mm = sum_force_y / report.total_probe_force_newtons;
        }

        return report;
    }

    static void print_report(const DftAuditReport& r, const std::vector<TestPointRecord>& tps) {
        std::cout << "\n====================================================================\n";
        std::cout << "         ЗВЕДЕНИЙ ВИРОБНИЧИЙ ЗВІТ ТЕСТОПРИДАТНОСТІ (DFT & ICT)      \n";
        std::cout << "====================================================================\n";
        std::cout << std::format(" Загальна кількість ланцюгів проекту : {}\n", r.total_nets);
        std::cout << std::format(" Ланцюгів із тестовими точками       : {} ({:.1f}%)\n",
                                 r.covered_nets, (static_cast<float>(r.covered_nets) / r.total_nets) * 100.0f);
        std::cout << std::format(" Інтегральний зважений індекс DFT    : {:.2f}% (Ціль >= 90.0%)\n", r.dft_weighted_score);
        std::cout << "--------------------------------------------------------------------\n";
        std::cout << " Покриття за класами ланцюгів:\n";
        std::cout << std::format("   • POWER      : {:2} / {:2} ({:5.1f}%) [Норма: 100%]\n",
                                 r.power_nets_covered, r.power_nets_total,
                                 r.power_nets_total ? (static_cast<float>(r.power_nets_covered) / r.power_nets_total) * 100.0f : 100.0f);
        std::cout << std::format("   • RESET      : {:2} / {:2} ({:5.1f}%) [Норма: 100%]\n",
                                 r.reset_nets_covered, r.reset_nets_total,
                                 r.reset_nets_total ? (static_cast<float>(r.reset_nets_covered) / r.reset_nets_total) * 100.0f : 100.0f);
        std::cout << std::format("   • ANALOG     : {:2} / {:2} ({:5.1f}%)\n",
                                 r.analog_nets_covered, r.analog_nets_total,
                                 r.analog_nets_total ? (static_cast<float>(r.analog_nets_covered) / r.analog_nets_total) * 100.0f : 100.0f);
        std::cout << std::format("   • CLOCK      : {:2} / {:2} ({:5.1f}%)\n",
                                 r.clock_nets_covered, r.clock_nets_total,
                                 r.clock_nets_total ? (static_cast<float>(r.clock_nets_covered) / r.clock_nets_total) * 100.0f : 100.0f);
        std::cout << "--------------------------------------------------------------------\n";
        std::cout << std::format(" Порушення зазорів / колізії         : {}\n", r.clearance_violations);
        std::cout << std::format(" Точки на верхньому шарі (Top)       : {}\n", r.layer_violations);
        std::cout << std::format(" Небезпечні швидкісні відводи        : {}\n", r.high_speed_stubs_flagged);
        std::cout << "--------------------------------------------------------------------\n";
        std::cout << std::format(" Сумарне зусилля стиснення ложа      : {:.1f} Н ({:.2f} кгс)\n",
                                 r.total_probe_force_newtons, r.total_probe_force_newtons / 9.80665f);
        std::cout << std::format(" Центр механічного тиску ложа        : X = {:.2f} мм, Y = {:.2f} мм\n",
                                 r.center_of_force_x_mm, r.center_of_force_y_mm);
        std::cout << "====================================================================\n\n";

        std::cout << "ФРАГМЕНТ ТАБЛИЦІ СВЕРДЛІННЯ КОНДУКТОРА (ICT DRILL & WIRING MAP):\n";
        std::cout << "----------------------------------------------------------------------------------------\n";
        std::cout << std::format("{:<8} | {:<16} | {:<8} | {:<8} | {:<8} | {:<26}\n",
                                 "Мітка", "Електричний ланцюг", "X (мм)", "Y (мм)", "D (мм)", "Рекомендований зонд (Probe)");
        std::cout << "----------------------------------------------------------------------------------------\n";
        const size_t limit = std::min(tps.size(), size_t{10});
        for (size_t i = 0; i < limit; ++i) {
            std::cout << std::format("{:<8} | {:<16} | {:8.3f} | {:8.3f} | {:8.2f} | {:<26}\n",
                                     tps[i].label, tps[i].net_name, tps[i].x_mm, tps[i].y_mm,
                                     tps[i].diameter_mm, tip_to_string(tps[i].recommended_tip));
        }
        std::cout << "----------------------------------------------------------------------------------------\n";
    }
};

} // namespace dft::core
