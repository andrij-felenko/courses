#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <expected>
#include <span>

namespace pdn {

constexpr double SPEED_OF_LIGHT_M_S = 299792458.0;
constexpr double VACUUM_PERMEABILITY_H_M = 4.0 * std::numbers::pi * 1e-7;

enum class Topology : uint8_t {
    FarTrace = 0,
    EndVia,
    SideVia,
    DoubleSideVia,
    ViaInPadTop,
    BgaBottomViPPO,
    Count
};

constexpr std::string_view get_topology_description(Topology top) noexcept {
    switch (top) {
        case Topology::FarTrace:        return "1. Far Traces (Віддалений монтаж, довгі траси l=4.0мм, s=3.5мм)";
        case Topology::EndVia:          return "2. End Vias (Торцеві перехідні отвори за контактними падами)";
        case Topology::SideVia:         return "3. Side Vias (Бічні перехідні отвори з мінімальним зазором)";
        case Topology::DoubleSideVia:   return "4. Double Side Vias (Подвійні симетричні бічні вії, 4 отвори)";
        case Topology::ViaInPadTop:     return "5. Via-in-Pad Top (Технологія VIPPO на верхньому шарі L1)";
        case Topology::BgaBottomViPPO:  return "6. BGA Bottom VIPPO (Монтаж на звороті плати прямо під чіпом)";
        default:                        return "Невідома топологія";
    }
}

struct CapacitorSpec {
    std::string part_name;
    double capacitance_f{100e-9};
    double esr_ohms{0.018};
    double esl_henries{0.38e-9};
    double length_m{0.0010};
    double width_m{0.0005};
    double pad_len_m{0.0005};
    double pad_width_m{0.0006};
};

struct StackupSpec {
    double dielectric_er{4.2};
    double h_to_gnd_plane_m{0.00012};
    double h_to_pwr_plane_m{0.00060};
    double total_board_thickness_m{0.00160};
    double via_drill_diameter_m{0.00025};
    double copper_thickness_m{0.000035};
};

struct AnalysisReport {
    double l_esl_nh{0.0};
    double l_pads_nh{0.0};
    double l_traces_nh{0.0};
    double l_vias_nh{0.0};
    double l_spread_nh{0.0};
    double l_total_mount_nh{0.0};
    double srf_frequency_mhz{0.0};
    double z_at_srf_mohms{0.0};
    double r_eff_100mhz_mm{0.0};
    double r_eff_500mhz_mm{0.0};
    double r_eff_1ghz_mm{0.0};
};

class DecouplingLoopEngine {
public:
    static double calc_rect_inductance(double length_m, double width_m, double thickness_m) noexcept {
        if (length_m <= 0.0 || width_m <= 0.0) return 0.0;
        const double wt = width_m + thickness_m;
        const double ratio = 2.0 * length_m / wt;
        if (ratio <= 0.0) return 0.0;
        const double term = std::log(ratio) + 0.5 + 0.2235 * (wt / length_m);
        return (VACUUM_PERMEABILITY_H_M * length_m / (2.0 * std::numbers::pi)) * term;
    }

    static double calc_via_self_inductance(double height_m, double radius_m) noexcept {
        if (height_m <= 0.0 || radius_m <= 0.0) return 0.0;
        const double ratio = 2.0 * height_m / radius_m;
        const double term = std::log(ratio + std::sqrt(1.0 + ratio * ratio))
                          - std::sqrt(1.0 + 1.0 / (ratio * ratio))
                          + (radius_m / (2.0 * height_m)) + 0.25;
        return (VACUUM_PERMEABILITY_H_M * height_m / (2.0 * std::numbers::pi)) * term;
    }

    static double calc_via_mutual_inductance(double height_m, double pitch_m) noexcept {
        if (height_m <= 0.0 || pitch_m <= 0.0) return 0.0;
        const double hs = height_m / pitch_m;
        const double sh = pitch_m / height_m;
        const double term = std::log(hs + std::sqrt(1.0 + hs * hs)) - std::sqrt(1.0 + sh * sh) + sh;
        return (VACUUM_PERMEABILITY_H_M * height_m / (2.0 * std::numbers::pi)) * term;
    }

    static double calc_spreading_inductance(double plane_gap_m, double via_radius_m, double pitch_m) noexcept {
        if (plane_gap_m <= 0.0 || via_radius_m <= 0.0 || pitch_m <= 2.0 * via_radius_m) return 0.0;
        return (VACUUM_PERMEABILITY_H_M * plane_gap_m / std::numbers::pi) * std::log(pitch_m / (2.0 * via_radius_m));
    }

    static double calc_effective_radius(double frequency_hz, double er, double safety_factor) noexcept {
        if (frequency_hz <= 0.0 || er <= 0.0 || safety_factor <= 0.0) return 0.0;
        const double v_propagation = SPEED_OF_LIGHT_M_S / std::sqrt(er);
        return v_propagation / (2.0 * std::numbers::pi * frequency_hz * safety_factor);
    }

    static std::expected<AnalysisReport, std::string> analyze_topology(
        const CapacitorSpec& cap, const StackupSpec& pcb, Topology topology) noexcept
    {
        if (cap.capacitance_f <= 0.0) return std::unexpected("Ємність конденсатора має бути додатною величиною");
        if (pcb.dielectric_er <= 1.0) return std::unexpected("Діелектрична проникність має бути більшою за 1.0");

        AnalysisReport report{};
        const double via_r = pcb.via_drill_diameter_m / 2.0;
        double l_pads = 0.0;
        double l_traces = 0.0;
        double l_vias = 0.0;
        double l_spread = 0.0;
        const double h_gnd = pcb.h_to_gnd_plane_m;
        const double h_pwr = pcb.h_to_pwr_plane_m;
        double d_planes = std::abs(pcb.h_to_pwr_plane_m - pcb.h_to_gnd_plane_m);
        if (d_planes < 1e-5) d_planes = 0.0001;

        switch (topology) {
            case Topology::FarTrace: {
                constexpr double tr_len = 0.0040;
                constexpr double tr_w = 0.00025;
                constexpr double via_pitch = 0.0035;
                l_pads = 2.0 * calc_rect_inductance(cap.pad_len_m, cap.pad_width_m, pcb.copper_thickness_m);
                l_traces = 2.0 * calc_rect_inductance(tr_len, tr_w, pcb.copper_thickness_m);
                const double l_vg = calc_via_self_inductance(h_gnd, via_r);
                const double l_vp = calc_via_self_inductance(h_pwr, via_r);
                const double m_v = calc_via_mutual_inductance((h_gnd + h_pwr) / 2.0, via_pitch);
                l_vias = l_vg + l_vp - 2.0 * m_v;
                l_spread = calc_spreading_inductance(d_planes, via_r, via_pitch);
                break;
            }
            case Topology::EndVia: {
                const double via_pitch = cap.length_m + 2.0 * via_r + 0.00020;
                l_pads = 2.0 * calc_rect_inductance(cap.pad_len_m, cap.pad_width_m, pcb.copper_thickness_m);
                l_traces = 2.0 * calc_rect_inductance(0.00030, cap.pad_width_m, pcb.copper_thickness_m);
                const double l_vg = calc_via_self_inductance(h_gnd, via_r);
                const double l_vp = calc_via_self_inductance(h_pwr, via_r);
                const double m_v = calc_via_mutual_inductance((h_gnd + h_pwr) / 2.0, via_pitch);
                l_vias = l_vg + l_vp - 2.0 * m_v;
                l_spread = calc_spreading_inductance(d_planes, via_r, via_pitch);
                break;
            }
            case Topology::SideVia: {
                const double via_pitch = cap.width_m + 2.0 * via_r + 0.00015;
                l_pads = 2.0 * calc_rect_inductance(cap.pad_len_m, cap.pad_width_m, pcb.copper_thickness_m);
                l_traces = 2.0 * calc_rect_inductance(0.00015, cap.pad_width_m, pcb.copper_thickness_m);
                const double l_vg = calc_via_self_inductance(h_gnd, via_r);
                const double l_vp = calc_via_self_inductance(h_pwr, via_r);
                const double m_v = calc_via_mutual_inductance((h_gnd + h_pwr) / 2.0, via_pitch);
                l_vias = l_vg + l_vp - 2.0 * m_v;
                l_spread = calc_spreading_inductance(d_planes, via_r, via_pitch);
                break;
            }
            case Topology::DoubleSideVia: {
                const double via_pitch = cap.width_m + 2.0 * via_r + 0.00015;
                l_pads = 2.0 * calc_rect_inductance(cap.pad_len_m, cap.pad_width_m, pcb.copper_thickness_m);
                l_traces = 0.5 * calc_rect_inductance(0.00015, cap.pad_width_m, pcb.copper_thickness_m);
                const double l_vg = calc_via_self_inductance(h_gnd, via_r);
                const double l_vp = calc_via_self_inductance(h_pwr, via_r);
                const double m_v = calc_via_mutual_inductance((h_gnd + h_pwr) / 2.0, via_pitch);
                l_vias = (l_vg + l_vp - 2.0 * m_v) * 0.52;
                l_spread = calc_spreading_inductance(d_planes, via_r, via_pitch) * 0.5;
                break;
            }
            case Topology::ViaInPadTop: {
                const double via_pitch = cap.length_m - cap.pad_len_m;
                l_pads = 0.5 * calc_rect_inductance(cap.pad_len_m, cap.pad_width_m, pcb.copper_thickness_m);
                l_traces = 0.0;
                const double l_vg = calc_via_self_inductance(h_gnd, via_r);
                const double l_vp = calc_via_self_inductance(h_pwr, via_r);
                const double m_v = calc_via_mutual_inductance((h_gnd + h_pwr) / 2.0, via_pitch);
                l_vias = l_vg + l_vp - 2.0 * m_v;
                l_spread = calc_spreading_inductance(d_planes, via_r, via_pitch);
                break;
            }
            case Topology::BgaBottomViPPO: {
                constexpr double via_pitch = 0.00080;
                const double h_bot_gnd = pcb.total_board_thickness_m - pcb.h_to_gnd_plane_m;
                const double h_bot_pwr = pcb.total_board_thickness_m - pcb.h_to_pwr_plane_m;
                l_pads = 0.3 * calc_rect_inductance(cap.pad_len_m, cap.pad_width_m, pcb.copper_thickness_m);
                l_traces = 0.0;
                const double l_vg = calc_via_self_inductance(h_bot_gnd, via_r);
                const double l_vp = calc_via_self_inductance(h_bot_pwr, via_r);
                const double m_v = calc_via_mutual_inductance((h_bot_gnd + h_bot_pwr) / 2.0, via_pitch);
                l_vias = l_vg + l_vp - 2.0 * m_v;
                l_spread = calc_spreading_inductance(d_planes, via_r, via_pitch);
                break;
            }
            default:
                return std::unexpected("Невідома конфігурація топології");
        }

        report.l_esl_nh = cap.esl_henries * 1e9;
        report.l_pads_nh = l_pads * 1e9;
        report.l_traces_nh = l_traces * 1e9;
        report.l_vias_nh = l_vias * 1e9;
        report.l_spread_nh = l_spread * 1e9;
        report.l_total_mount_nh = (cap.esl_henries + l_pads + l_traces + l_vias + l_spread) * 1e9;

        const double l_total_h = report.l_total_mount_nh * 1e-9;
        if (l_total_h > 0.0 && cap.capacitance_f > 0.0) {
            report.srf_frequency_mhz = (1.0 / (2.0 * std::numbers::pi * std::sqrt(l_total_h * cap.capacitance_f))) / 1e6;
        }

        report.z_at_srf_mohms = cap.esr_ohms * 1000.0;
        report.r_eff_100mhz_mm = calc_effective_radius(100e6, pcb.dielectric_er, 4.0) * 1000.0;
        report.r_eff_500mhz_mm = calc_effective_radius(500e6, pcb.dielectric_er, 4.0) * 1000.0;
        report.r_eff_1ghz_mm = calc_effective_radius(1e9, pcb.dielectric_er, 4.0) * 1000.0;

        return report;
    }
};

} // namespace pdn

int main() {
    using namespace pdn;

    const CapacitorSpec cap0402{
        .part_name = "0402 100nF 6.3V X7R",
        .capacitance_f = 100e-9,
        .esr_ohms = 0.018,
        .esl_henries = 0.38e-9,
        .length_m = 0.0010,
        .width_m = 0.0005,
        .pad_len_m = 0.0005,
        .pad_width_m = 0.0006
    };

    const StackupSpec pcb6layer{
        .dielectric_er = 4.2,
        .h_to_gnd_plane_m = 0.00012,
        .h_to_pwr_plane_m = 0.00060,
        .total_board_thickness_m = 0.00160,
        .via_drill_diameter_m = 0.00025,
        .copper_thickness_m = 0.000035
    };

    std::cout << "==================================================================================================\n"
              << "  C++20 АНАЛІЗ ІНДУКТИВНОСТІ МОНТАЖУ PDN (" << cap0402.part_name << ")\n"
              << "  Стек: 6 шарів, плата " << pcb6layer.total_board_thickness_m * 1000.0 << " мм, "
              << "L2 GND=" << pcb6layer.h_to_gnd_plane_m * 1000.0 << " мм, Er=" << pcb6layer.dielectric_er << "\n"
              << "==================================================================================================\n\n";

    std::cout << std::left << std::setw(53) << "Топологія трасування" << " | "
              << std::right << std::setw(6) << "L_pads" << " | "
              << std::setw(6) << "L_trc" << " | "
              << std::setw(6) << "L_vias" << " | "
              << std::setw(6) << "L_sprd" << " | "
              << std::setw(8) << "L_TOTAL" << " | "
              << std::setw(9) << "SRF (MHz)" << "\n";
    std::cout << std::string(53, '-') << "-+--------+--------+--------+--------+----------+-----------\n";

    for (uint8_t i = 0; i < static_cast<uint8_t>(Topology::Count); ++i) {
        const auto top = static_cast<Topology>(i);
        auto res = DecouplingLoopEngine::analyze_topology(cap0402, pcb6layer, top);
        if (!res) {
            std::cerr << "Помилка аналізу: " << res.error() << "\n";
            continue;
        }

        std::cout << std::left << std::setw(53) << get_topology_description(top) << " | "
                  << std::right << std::fixed << std::setprecision(2)
                  << std::setw(6) << res->l_pads_nh << " | "
                  << std::setw(6) << res->l_traces_nh << " | "
                  << std::setw(6) << res->l_vias_nh << " | "
                  << std::setw(6) << res->l_spread_nh << " | "
                  << std::setw(6) << res->l_total_mount_nh << " нГн | "
                  << std::setprecision(1) << std::setw(7) << res->srf_frequency_mhz << " МГц\n";
    }

    auto side_res = DecouplingLoopEngine::analyze_topology(cap0402, pcb6layer, Topology::SideVia);
    if (side_res) {
        std::cout << "\n--------------------------------------------------------------------------------------------------\n"
                  << "  Ефективний просторовий радіус розв'язки (Er=" << pcb6layer.dielectric_er << ", k=4):\n"
                  << "    • 100 МГц -> r_eff = " << std::fixed << std::setprecision(1) << side_res->r_eff_100mhz_mm << " мм\n"
                  << "    • 500 МГц -> r_eff = " << side_res->r_eff_500mhz_mm << " мм\n"
                  << "    • 1.0 ГГц -> r_eff = " << side_res->r_eff_1ghz_mm << " мм\n"
                  << "==================================================================================================\n";
    }

    return 0;
}
