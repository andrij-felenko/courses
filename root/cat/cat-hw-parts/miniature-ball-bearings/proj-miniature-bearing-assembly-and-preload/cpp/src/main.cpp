#include "bearing_validator.hpp"
#include <iostream>

int main() {
    BearingGeometry bearing_608{
        .model = "608 (8x22x7 мм)",
        .inner_diameter_mm = 8.0,
        .outer_diameter_mm = 22.0,
        .width_mm = 7.0,
        .initial_clearance_um = 8.0,
        .c0_stat_n = 1350.0
    };

    BearingAssemblyValidator validator(bearing_608);

    FitTolerance normal_fit{
        .shaft_dev_min_um = 2.0,
        .shaft_dev_max_um = 6.0,
        .housing_dev_min_um = 0.0,
        .housing_dev_max_um = 12.0
    };

    auto report = validator.validate(normal_fit);

    std::cout << "====================================================\n";
    std::cout << " Валідація монтажу підшипника " << bearing_608.model << "\n";
    std::cout << "====================================================\n";
    std::cout << "Макс. натяг по валу: " << report.shaft_interference_max_um << " мкм\n";
    std::cout << "Звуження зазору:     " << report.clearance_reduction_um << " мкм\n";
    std::cout << "Залишковий зазор:    " << report.residual_clearance_um << " мкм\n";
    std::cout << "Статус вузла:        " << (report.is_valid ? "СХВАЛЕНО" : "ВІДХИЛЕНО") << "\n";
    std::cout << "Висновок:            " << report.summary_message << "\n";
    std::cout << "====================================================\n";

    return report.is_valid ? 0 : 1;
}
