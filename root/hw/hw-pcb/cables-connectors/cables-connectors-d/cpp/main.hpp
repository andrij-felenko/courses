#include <iostream>
#include <expected>
#include <string_view>

struct HarnessConfig {
    double wire_resistance_ohm{0.0};
    double contact_resistance_ohm{0.0};
    int contacts_per_rail{2};
    double load_current_a{0.0};
    double v_il_max{0.80};
    double v_ol_max{0.15};
};

struct HarnessAnalysis {
    double v_drop_loop_v{0.0};
    double ground_shift_v{0.0};
    double noise_margin_v{0.0};
    bool is_reliable{false};
};

constexpr auto analyze_harness(const HarnessConfig& cfg) noexcept -> HarnessAnalysis {
    const double r_rail = cfg.wire_resistance_ohm + (cfg.contact_resistance_ohm * cfg.contacts_per_rail);
    const double r_loop = 2.0 * r_rail;
    
    const double v_drop = cfg.load_current_a * r_loop;
    const double gnd_shift = cfg.load_current_a * r_rail;
    const double margin = cfg.v_il_max - (cfg.v_ol_max + gnd_shift);
    
    return {
        .v_drop_loop_v = v_drop,
        .ground_shift_v = gnd_shift,
        .noise_margin_v = margin,
        .is_reliable = (margin >= 0.20 && gnd_shift <= 0.30)
    };
}
