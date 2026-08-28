#include <iostream>
#include <iomanip>
#include <string>
#include <string_view>
#include <vector>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <optional>
#include <format>

enum class PadType {
    Rectangular,
    Circular,
    RoundedRect,
    Obround,
    HomePlate,
    ThermalExposed,
    ThroughHoleTHR
};

struct StencilConfig {
    double foil_thickness_mm{0.120};
    bool has_nano_coating{false};
    double target_thermal_coverage{0.60};
    double min_web_width_mm{0.30};

    [[nodiscard]] constexpr double area_ratio_threshold() const noexcept {
        return has_nano_coating ? 0.55 : 0.66;
    }
};

struct ComponentPad {
    std::string component_name;
    std::string footprint_name;
    PadType pad_type{PadType::Rectangular};
    double width_mm{0.0};
    double length_mm{0.0};
    double corner_radius_mm{0.0};
    double home_plate_cut_mm{0.0};
    /* Параметри Through-Hole Reflow */
    double pcb_thickness_mm{1.60};
    double hole_diameter_mm{0.0};
    double pin_diameter_mm{0.0};
};

struct ApertureEvaluation {
    double area_pad_mm2{0.0};
    double area_walls_mm2{0.0};
    double theoretical_volume_mm3{0.0};
    double area_ratio{0.0};
    double aspect_ratio{0.0};
    double transfer_efficiency{0.0};
    double expected_volume_mm3{0.0};
    bool pass_area_ratio{false};
    bool pass_aspect_ratio{false};

    /* Оптимізація редукції */
    double opt_width_mm{0.0};
    double opt_length_mm{0.0};
    double reduction_percent{0.0};

    /* Віконна решітка */
    int grid_nx{1};
    int grid_ny{1};
    double window_width_mm{0.0};
    double window_length_mm{0.0};
    double actual_coverage_percent{0.0};

    /* Through-Hole Reflow */
    double thr_paste_required_mm3{0.0};
    double thr_overprint_size_mm{0.0};
};

class StencilOptimizer {
public:
    [[nodiscard]] static ApertureEvaluation evaluate(const ComponentPad& pad, const StencilConfig& cfg) noexcept {
        ApertureEvaluation eval{};
        switch (pad.pad_type) {
            case PadType::Rectangular:
                evaluate_rectangular(pad, cfg, eval);
                break;
            case PadType::Circular:
                evaluate_circular(pad, cfg, eval);
                break;
            case PadType::RoundedRect:
            case PadType::Obround:
                evaluate_rounded_rect(pad, cfg, eval);
                break;
            case PadType::HomePlate:
                evaluate_home_plate(pad, cfg, eval);
                break;
            case PadType::ThermalExposed:
                evaluate_thermal_pad(pad, cfg, eval);
                break;
            case PadType::ThroughHoleTHR:
                evaluate_thr_pin(pad, cfg, eval);
                break;
        }
        return eval;
    }

private:
    static void evaluate_rectangular(const ComponentPad& pad, const StencilConfig& cfg, ApertureEvaluation& eval) noexcept {
        const double w = pad.width_mm;
        const double l = pad.length_mm;
        const double t = cfg.foil_thickness_mm;

        eval.area_pad_mm2 = w * l;
        eval.area_walls_mm2 = 2.0 * (w + l) * t;
        eval.theoretical_volume_mm3 = eval.area_pad_mm2 * t;

        eval.area_ratio = eval.area_pad_mm2 / eval.area_walls_mm2;
        eval.aspect_ratio = std::min(w, l) / t;

        const double ar_thresh = cfg.area_ratio_threshold();
        eval.pass_area_ratio = (eval.area_ratio >= ar_thresh);
        eval.pass_aspect_ratio = (eval.aspect_ratio >= 1.50);

        const double k = cfg.has_nano_coating ? 14.0 : 11.0;
        const double ar0 = cfg.has_nano_coating ? 0.45 : 0.55;
        eval.transfer_efficiency = 0.96 / (1.0 + std::exp(-k * (eval.area_ratio - ar0)));
        eval.expected_volume_mm3 = eval.theoretical_volume_mm3 * eval.transfer_efficiency;

        const double opt_w = w * 0.90;
        const double opt_l = l * 0.90;
        const double opt_ar = (opt_w * opt_l) / (2.0 * (opt_w + opt_l) * t);

        if (opt_ar >= ar_thresh) {
            eval.opt_width_mm = opt_w;
            eval.opt_length_mm = opt_l;
            eval.reduction_percent = 19.0;
        } else {
            eval.opt_width_mm = w;
            eval.opt_length_mm = l;
            eval.reduction_percent = 0.0;
        }
    }

    static void evaluate_circular(const ComponentPad& pad, const StencilConfig& cfg, ApertureEvaluation& eval) noexcept {
        const double d = pad.width_mm;
        const double t = cfg.foil_thickness_mm;

        eval.area_pad_mm2 = (std::numbers::pi * d * d) / 4.0;
        eval.area_walls_mm2 = std::numbers::pi * d * t;
        eval.theoretical_volume_mm3 = eval.area_pad_mm2 * t;

        eval.area_ratio = d / (4.0 * t);
        eval.aspect_ratio = d / t;

        const double ar_thresh = cfg.area_ratio_threshold();
        eval.pass_area_ratio = (eval.area_ratio >= ar_thresh);
        eval.pass_aspect_ratio = (eval.aspect_ratio >= 1.50);

        const double k = cfg.has_nano_coating ? 14.0 : 11.0;
        const double ar0 = cfg.has_nano_coating ? 0.45 : 0.55;
        eval.transfer_efficiency = 0.96 / (1.0 + std::exp(-k * (eval.area_ratio - ar0)));
        eval.expected_volume_mm3 = eval.theoretical_volume_mm3 * eval.transfer_efficiency;

        eval.opt_width_mm = d;
        eval.opt_length_mm = d;
        eval.reduction_percent = 0.0;
    }

    static void evaluate_rounded_rect(const ComponentPad& pad, const StencilConfig& cfg, ApertureEvaluation& eval) noexcept {
        const double w = pad.width_mm;
        const double l = pad.length_mm;
        double r = pad.corner_radius_mm;
        const double t = cfg.foil_thickness_mm;

        r = std::min({r, w / 2.0, l / 2.0});

        eval.area_pad_mm2 = (w * l) - (4.0 - std::numbers::pi) * (r * r);
        const double perimeter = 2.0 * (w + l) - (8.0 - 2.0 * std::numbers::pi) * r;
        eval.area_walls_mm2 = perimeter * t;
        eval.theoretical_volume_mm3 = eval.area_pad_mm2 * t;

        eval.area_ratio = eval.area_pad_mm2 / eval.area_walls_mm2;
        eval.aspect_ratio = std::min(w, l) / t;

        const double ar_thresh = cfg.area_ratio_threshold();
        eval.pass_area_ratio = (eval.area_ratio >= ar_thresh);
        eval.pass_aspect_ratio = (eval.aspect_ratio >= 1.50);

        const double k = cfg.has_nano_coating ? 14.0 : 11.0;
        const double ar0 = cfg.has_nano_coating ? 0.45 : 0.55;
        eval.transfer_efficiency = 0.97 / (1.0 + std::exp(-k * (eval.area_ratio - ar0)));
        eval.expected_volume_mm3 = eval.theoretical_volume_mm3 * eval.transfer_efficiency;

        eval.opt_width_mm = w;
        eval.opt_length_mm = l;
        eval.reduction_percent = 0.0;
    }

    static void evaluate_home_plate(const ComponentPad& pad, const StencilConfig& cfg, ApertureEvaluation& eval) noexcept {
        const double w = pad.width_mm;
        const double l = pad.length_mm;
        double c = pad.home_plate_cut_mm > 0.0 ? pad.home_plate_cut_mm : w * 0.35;
        const double t = cfg->foil_thickness_mm;

        if (c >= l) c = l * 0.5;

        eval.area_pad_mm2 = (w * l) - (0.5 * w * c);
        const double hypotenuse = std::sqrt(c * c + (w / 2.0) * (w / 2.0));
        const double perimeter = 2.0 * (l - c) + w + 2.0 * hypotenuse;
        eval.area_walls_mm2 = perimeter * t;
        eval.theoretical_volume_mm3 = eval.area_pad_mm2 * t;

        eval.area_ratio = eval.area_pad_mm2 / eval.area_walls_mm2;
        eval.aspect_ratio = std::min(w, l) / t;

        const double ar_thresh = cfg.area_ratio_threshold();
        eval.pass_area_ratio = (eval.area_ratio >= ar_thresh);
        eval.pass_aspect_ratio = (eval.aspect_ratio >= 1.50);

        const double k = cfg.has_nano_coating ? 14.0 : 11.0;
        const double ar0 = cfg.has_nano_coating ? 0.45 : 0.55;
        eval.transfer_efficiency = 0.96 / (1.0 + std::exp(-k * (eval.area_ratio - ar0)));
        eval.expected_volume_mm3 = eval.theoretical_volume_mm3 * eval.transfer_efficiency;

        eval.opt_width_mm = w;
        eval.opt_length_mm = l;
        eval.reduction_percent = (0.5 * w * c) / (w * l) * 100.0;
    }

    static void evaluate_thermal_pad(const ComponentPad& pad, const StencilConfig& cfg, ApertureEvaluation& eval) noexcept {
        const double w = pad.width_mm;
        const double l = pad.length_mm;
        const double t = cfg.foil_thickness_mm;
        const double cov = cfg.target_thermal_coverage;
        const double web = cfg.min_web_width_mm;

        eval.area_pad_mm2 = w * l;
        eval.theoretical_volume_mm3 = eval.area_pad_mm2 * t;

        int nx = std::clamp(static_cast<int>(std::floor(w / 1.5)), 2, 5);
        int ny = std::clamp(static_cast<int>(std::floor(l / 1.5)), 2, 5);

        eval.grid_nx = nx;
        eval.grid_ny = ny;

        const double target_win_sum = eval.area_pad_mm2 * cov;
        const double single_win_area = target_win_sum / static_cast<double>(nx * ny);

        const double aspect = w / l;
        double win_l = std::sqrt(single_win_area / aspect);
        double win_w = win_l * aspect;

        const double max_w = (w - (nx - 1) * web) / static_cast<double>(nx);
        const double max_l = (l - (ny - 1) * web) / static_cast<double>(ny);

        win_w = std::min(win_w, max_w);
        win_l = std::min(win_l, max_l);

        eval.window_width_mm = win_w;
        eval.window_length_mm = win_l;

        const double actual_paste_area = static_cast<double>(nx * ny) * (win_w * win_l);
        eval.actual_coverage_percent = (actual_paste_area / eval.area_pad_mm2) * 100.0;

        const double a_win_pad = win_w * win_l;
        const double a_win_walls = 2.0 * (win_w + win_l) * t;
        eval.area_ratio = a_win_pad / a_win_walls;
        eval.aspect_ratio = std::min(win_w, win_l) / t;

        const double ar_thresh = cfg.area_ratio_threshold();
        eval.pass_area_ratio = (eval.area_ratio >= ar_thresh);
        eval.pass_aspect_ratio = (eval.aspect_ratio >= 1.50);

        eval.transfer_efficiency = 0.95;
        eval.expected_volume_mm3 = actual_paste_area * t * eval.transfer_efficiency;
    }

    static void evaluate_thr_pin(const ComponentPad& pad, const StencilConfig& cfg, ApertureEvaluation& eval) noexcept {
        const double d_hole = pad.hole_diameter_mm;
        const double d_pin = pad.pin_diameter_mm;
        const double h_pcb = pad.pcb_thickness_mm;
        const double t_foil = cfg.foil_thickness_mm;

        const double v_hole = std::numbers::pi * std::pow(d_hole / 2.0, 2.0) * h_pcb;
        const double v_pin = std::numbers::pi * std::pow(d_pin / 2.0, 2.0) * h_pcb;
        const double v_gap = v_hole - v_pin;

        const double v_fillet_top = 0.25 * v_gap;
        const double v_fillet_bot = 0.25 * v_gap;
        const double v_solder_target = v_gap + v_fillet_top + v_fillet_bot;

        eval.thr_paste_required_mm3 = 2.0 * v_solder_target;
        const double required_area = eval.thr_paste_required_mm3 / t_foil;
        eval.thr_overprint_size_mm = std::sqrt(required_area);

        eval.area_pad_mm2 = required_area;
        eval.area_walls_mm2 = 4.0 * eval.thr_overprint_size_mm * t_foil;
        eval.area_ratio = eval.area_pad_mm2 / eval.area_walls_mm2;
        eval.aspect_ratio = eval.thr_overprint_size_mm / t_foil;
        eval.pass_area_ratio = true;
        eval.pass_aspect_ratio = true;
        eval.transfer_efficiency = 0.95;
        eval.expected_volume_mm3 = eval.thr_paste_required_mm3 * 0.95;
    }
};

void print_cpp_report(const std::vector<ComponentPad>& pads, const StencilConfig& cfg) {
    std::cout << "========================================================================================================\n";
    std::cout << "                  ЗВІТ ВАЛІДАЦІЇ ТРАФАРЕТНИХ АПЕРТУР ЗА СТАНДАРТОМ IPC-7525 (C++20)\n";
    std::cout << std::format("  Параметри фольги: Товщина = {:.3f} мм ({} мкм), Нанопокриття: {}\n", 
                             cfg.foil_thickness_mm, static_cast<int>(cfg.foil_thickness_mm * 1000.0),
                             cfg.has_nano_coating ? "ТАК (Поріг AR >= 0.55)" : "НІ (Поріг AR >= 0.66)");
    std::cout << "========================================================================================================\n";
    std::cout << std::format("{:<10} {:<12} {:<8} {:<8} {:<7} {:<7} {:<7} {:<8} {:<12} {:<12}\n",
                             "Компонент", "Корпус", "Розмір", "AR", "AR-Стан", "AS", "AS-Стан", "TE %", "Очік. V(нл)", "Оптимізація");
    std::cout << "--------------------------------------------------------------------------------------------------------\n";

    for (const auto& pad : pads) {
        const auto ev = StencilOptimizer::evaluate(pad, cfg);

        std::string dim_str;
        if (pad.pad_type == PadType::Circular) {
            dim_str = std::format("D{:.2f}", pad.width_mm);
        } else {
            dim_str = std::format("{:.2f}x{:.2f}", pad.width_mm, pad.length_mm);
        }

        std::string opt_str;
        if (pad.pad_type == PadType::ThermalExposed) {
            opt_str = std::format("Grid {}x{} ({:.0f}%)", ev.grid_nx, ev.grid_ny, ev.actual_coverage_percent);
        } else if (pad.pad_type == PadType::ThroughHoleTHR) {
            opt_str = std::format("Overprint {:.2f}", ev.thr_overprint_size_mm);
        } else if (pad.pad_type == PadType::HomePlate) {
            opt_str = std::format("HomePlate -{:.0f}%", ev.reduction_percent);
        } else if (ev.reduction_percent > 0.1) {
            opt_str = std::format("-{:.0f}% Редукція", ev.reduction_percent);
        } else {
            opt_str = "1:1 Без змін";
        }

        std::cout << std::format("{:<10} {:<12} {:<8} {:<8.3f} {:<7} {:<7.2f} {:<7} {:<7.1f}% {:<12.3f} {:<12}\n",
                                 pad.component_name,
                                 pad.footprint_name,
                                 dim_str,
                                 ev.area_ratio,
                                 ev.pass_area_ratio ? "PASS" : "FAIL",
                                 ev.aspect_ratio,
                                 ev.pass_aspect_ratio ? "PASS" : "FAIL",
                                 ev.transfer_efficiency * 100.0,
                                 ev.expected_volume_mm3 * 1000.0,
                                 opt_str);
    }
    std::cout << "========================================================================================================\n";
}

int main() {
    const StencilConfig cfg_standard{
        .foil_thickness_mm = 0.120,
        .has_nano_coating = false,
        .target_thermal_coverage = 0.60,
        .min_web_width_mm = 0.30
    };

    const StencilConfig cfg_nano{
        .foil_thickness_mm = 0.120,
        .has_nano_coating = true,
        .target_thermal_coverage = 0.60,
        .min_web_width_mm = 0.30
    };

    const std::vector<ComponentPad> bom_pads = {
        { "C101", "C_0201", PadType::Rectangular, 0.30, 0.30, 0.05 },
        { "R105", "R_0402", PadType::RoundedRect, 0.50, 0.55, 0.10 },
        { "C106", "C_0603", PadType::HomePlate, 0.80, 0.90, 0.0, 0.30 },
        { "U2", "QFP-48_P0.5", PadType::Rectangular, 0.25, 1.20, 0.05 },
        { "U1_Signals", "QFN-32_P0.4", PadType::Rectangular, 0.20, 0.80, 0.04 },
        { "U1_Thermal", "QFN-32_EP", PadType::ThermalExposed, 4.50, 4.50, 0.0 },
        { "U3_BGA", "BGA-256_P0.5", PadType::Circular, 0.28, 0.0, 0.0 },
        { "J1_Power", "THR_HDR_1x2", PadType::ThroughHoleTHR, 2.00, 2.00, 0.0, 0.0, 1.60, 1.10, 0.64 }
    };

    std::cout << "\n[ТЕСТ C++20: СТАНДАРТНИЙ ТРАФАРЕТ 120 МКМ]\n";
    print_cpp_report(bom_pads, cfg_standard);

    std::cout << "\n[ТЕСТ C++20: ТРАФАРЕТ З НАНОПОКРИТТЯМ NANO-COATING]\n";
    print_cpp_report(bom_pads, cfg_nano);

    return 0;
}
