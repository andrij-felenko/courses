#include <expected>

struct ResistanceResult {
    double r_eff{0.0};
    double commute_time{0.0};
};

std::expected<ResistanceResult, WalkStatus> calculate_effective_resistance(
    const GraphSpec& graph,
    uint32_t u,
    uint32_t v
);
