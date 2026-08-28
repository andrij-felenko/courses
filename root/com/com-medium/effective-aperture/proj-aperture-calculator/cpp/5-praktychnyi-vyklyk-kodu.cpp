#include "aperture_calc.hpp"
#include <array>

int main() {
    const std::array<rf::AntennaParams, 3> system_antennas{{
        {.frequency_hz = 2.4e9,  .gain_dbi = 2.15, .efficiency = 1.00}, // Dipole 2.4 GHz
        {.frequency_hz = 12.0e9, .gain_dbi = 36.0, .efficiency = 0.65}, // Ku-band Dish 60cm
        {.frequency_hz = 70.0e9, .gain_dbi = 45.0, .efficiency = 0.55}  // E-band Millimeter Dish
    }};

    std::cout << "=== ЗВІТ ЕФЕКТИВНОЇ АПЕРТУРИ СИСТЕМИ ===\n\n";
    rf::print_aperture_report(system_antennas);

    return 0;
}
