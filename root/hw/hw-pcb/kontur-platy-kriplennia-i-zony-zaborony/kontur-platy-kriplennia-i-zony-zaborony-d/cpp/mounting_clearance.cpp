// mounting_clearance.cpp — Ідіоматичний розрахунок зон кріплення на C++20
#include <iostream>
#include <numbers>
#include <optional>
#include <string_view>
#include <format>

enum class ScrewSize {
    M2,
    M2_5,
    M3,
    M4
};

struct FastenerProfile {
    double drill_diameter;      // Діаметр отвору в платі, мм
    double head_diameter;       // Діаметр головки гвинта за DIN, мм
    double washer_diameter;     // Діаметр збільшеної шайби DIN 9021, мм
    double tool_envelope_dia;   // Діаметр інструмента затяжки, мм
    double copper_pullback;     // Мінімальний відступ міді від шайби, мм
};

[[nodiscard]] constexpr FastenerProfile get_fastener_profile(ScrewSize size) noexcept {
    switch (size) {
        case ScrewSize::M2:
            return {.drill_diameter = 2.2, .head_diameter = 3.8, .washer_diameter = 5.0,  .tool_envelope_dia = 7.0,  .copper_pullback = 0.5};
        case ScrewSize::M2_5:
            return {.drill_diameter = 2.7, .head_diameter = 4.5, .washer_diameter = 6.5,  .tool_envelope_dia = 8.5,  .copper_pullback = 0.6};
        case ScrewSize::M3:
            return {.drill_diameter = 3.2, .head_diameter = 5.5, .washer_diameter = 7.0,  .tool_envelope_dia = 10.0, .copper_pullback = 0.8};
        case ScrewSize::M4:
            return {.drill_diameter = 4.3, .head_diameter = 7.0, .washer_diameter = 9.0,  .tool_envelope_dia = 12.5, .copper_pullback = 1.0};
    }
    return {};
}

struct MountingKeepoutRadii {
    double cmp_keepout_radius;
    double copper_keepout_radius;
    double tool_clearance_radius;
};

[[nodiscard]] constexpr MountingKeepoutRadii calculate_mounting_keepouts(ScrewSize size, bool use_large_washer) noexcept {
    const auto prof = get_fastener_profile(size);
    const double effective_mech_dia = use_large_washer ? prof.washer_diameter : prof.head_diameter;
    
    return {
        .cmp_keepout_radius    = (effective_mech_dia / 2.0) + 0.3,
        .copper_keepout_radius = (effective_mech_dia / 2.0) + prof.copper_pullback,
        .tool_clearance_radius = prof.tool_envelope_dia / 2.0
    };
}

int main() {
    constexpr auto m3 = calculate_mounting_keepouts(ScrewSize::M3, true);
    std::cout << "Кріплення M3 із шайбою (C++20 розрахунок):\n";
    std::cout << std::format(" - Радіус заборони компонентів: {:>5.2f} мм\n", m3.cmp_keepout_radius);
    std::cout << std::format(" - Радіус відступу міді:        {:>5.2f} мм\n", m3.copper_keepout_radius);
    std::cout << std::format(" - Радіус конверта інструмента: {:>5.2f} мм\n", m3.tool_clearance_radius);
    return 0;
}
