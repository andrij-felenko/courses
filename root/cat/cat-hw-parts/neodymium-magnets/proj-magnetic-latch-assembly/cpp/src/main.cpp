#include "magnetic_latch_configurator.hpp"
#include <iostream>
#include <iomanip>

int main() {
    MagnetSpec magnet_n42{
        .grade = "NdFeB N42",
        .diameter_mm = 10.0,
        .thickness_mm = 3.0,
        .br_tesla = 1.30
    };

    const double glue_gap_mm = 0.15;
    const double epoxy_limit_mpa = 12.0;
    const double air_gap_mm = 0.10;

    std::cout << "===============================================================\n";
    std::cout << "  Валідація посадки неодимового магніту (" << magnet_n42.grade << " 10x3 мм)\n";
    std::cout << "===============================================================\n";

    for (auto mat : {HousingMaterial::Aluminum6061, HousingMaterial::PetgPrint}) {
        MagneticLatchConfigurator configurator(magnet_n42, mat);
        auto report = configurator.validate(glue_gap_mm, epoxy_limit_mpa, air_gap_mm);

        std::cout << "\nМатеріал: " << MagneticLatchConfigurator::get_material_name(mat) << "\n";
        std::cout << "---------------------------------------------------------------\n";
        std::cout << " - Індукція в зазорі (0.1 мм): " << std::fixed << std::setprecision(3)
                  << report.b_surface_tesla << " Тл\n";
        std::cout << " - Сила відриву:               " << std::fixed << std::setprecision(1)
                  << report.pull_force_n << " Н (≈ "
                  << (report.pull_force_n / 9.80665) << " кгс)\n";
        std::cout << " - CAD розмір гнізда:          Ø" << std::fixed << std::setprecision(2)
                  << report.pocket.pocket_dia_cad_mm << " x " << report.pocket.pocket_depth_mm << " мм\n";
        std::cout << " - Площа контакту з клеєм:     " << std::fixed << std::setprecision(1)
                  << report.pocket.glue_area_mm2 << " мм²\n";
        std::cout << " - Розрахункове напруження:    " << std::fixed << std::setprecision(2)
                  << report.shear_stress_mpa << " МПа\n";
        std::cout << " - Запас міцності шва:         " << std::fixed << std::setprecision(1)
                  << report.safety_factor << "\n";
        std::cout << " - Вердикт:                    " << (report.is_valid ? "СХВАЛЕНО" : "ВІДХИЛЕНО") << "\n";
        std::cout << " - Рекомендація:               " << report.notes << "\n";
    }
    std::cout << "===============================================================\n";

    return 0;
}
