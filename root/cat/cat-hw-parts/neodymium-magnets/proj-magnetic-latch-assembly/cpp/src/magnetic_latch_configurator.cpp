#include "magnetic_latch_configurator.hpp"
#include <cmath>
#include <sstream>
#include <iomanip>

namespace {
    constexpr double MU_0 = 4.0 * 3.14159265358979323846 * 1e-7;
    constexpr double PI = 3.14159265358979323846;
}

MagneticLatchConfigurator::MagneticLatchConfigurator(MagnetSpec magnet, HousingMaterial material)
    : magnet_(std::move(magnet)), material_(material) {}

std::string_view MagneticLatchConfigurator::get_material_name(HousingMaterial material) noexcept {
    switch (material) {
        case HousingMaterial::Aluminum6061: return "Алюміній 6061 (фрезерування)";
        case HousingMaterial::PetgPrint:    return "PETG пластик (FDM 3D-друк)";
        case HousingMaterial::AbsPrint:     return "ABS пластик (FDM 3D-друк)";
        case HousingMaterial::MildSteel:    return "Конструкційна сталь";
    }
    return "Невідомий матеріал";
}

double MagneticLatchConfigurator::compute_shrinkage_compensation() const noexcept {
    switch (material_) {
        case HousingMaterial::Aluminum6061:
            return 0.02; /* Допуск H8 на розточування */
        case HousingMaterial::PetgPrint:
            return 0.15; /* Радіальна усадка та похибка FDM друку */
        case HousingMaterial::AbsPrint:
            return 0.25; /* Підвищена усадка ABS */
        case HousingMaterial::MildSteel:
            return 0.02;
    }
    return 0.0;
}

double MagneticLatchConfigurator::compute_flux_density(double gap_mm) const noexcept {
    const double r = magnet_.diameter_mm / 2.0;
    const double l = magnet_.thickness_mm;
    const double z = (gap_mm < 0.0) ? 0.0 : gap_mm;

    const double term1 = (z + l) / std::sqrt(r * r + (z + l) * (z + l));
    const double term2 = (z == 0.0) ? 0.0 : (z / std::sqrt(r * r + z * z));

    return (magnet_.br_tesla / 2.0) * (term1 - term2);
}

double MagneticLatchConfigurator::compute_pull_force(double b_tesla) const noexcept {
    const double r = magnet_.diameter_mm / 2.0;
    const double area_m2 = (PI * r * r) * 1e-6;

    // Підсилення потоку для сталі (ефект магнітопроводу)
    const double steel_boost = (material_ == HousingMaterial::MildSteel) ? 1.6 : 1.0;
    return (b_tesla * b_tesla * area_m2 * steel_boost) / (2.0 * MU_0);
}

LatchValidationReport MagneticLatchConfigurator::validate(double target_glue_gap_mm,
                                                         double adhesive_shear_limit_mpa,
                                                         double air_gap_mm) const {
    LatchValidationReport report;

    const double compensation = compute_shrinkage_compensation();
    report.pocket.effective_glue_gap_mm = target_glue_gap_mm;
    report.pocket.pocket_dia_cad_mm = magnet_.diameter_mm + 2.0 * target_glue_gap_mm + compensation;
    report.pocket.pocket_depth_mm = magnet_.thickness_mm + 0.2; // Заглиблення 0.2 мм нижче площини

    const double pole_area = PI * (magnet_.diameter_mm / 2.0) * (magnet_.diameter_mm / 2.0);
    const double side_area = PI * magnet_.diameter_mm * magnet_.thickness_mm;
    report.pocket.glue_area_mm2 = pole_area + side_area;

    report.b_surface_tesla = compute_flux_density(air_gap_mm);
    report.pull_force_n = compute_pull_force(report.b_surface_tesla);

    if (report.pocket.glue_area_mm2 > 0.0) {
        report.shear_stress_mpa = report.pull_force_n / report.pocket.glue_area_mm2;
    }

    if (report.shear_stress_mpa > 1e-6) {
        report.safety_factor = adhesive_shear_limit_mpa / report.shear_stress_mpa;
    } else {
        report.safety_factor = 999.0;
    }

    std::ostringstream ss;
    if (report.safety_factor < 2.0) {
        report.is_valid = false;
        ss << "УВАГА: Недостатній запас міцності клейового шва ("
           << std::fixed << std::setprecision(1) << report.safety_factor
           << " < 2.0). Рекомендується збільшити діаметр або застосувати механічну завальцовку.";
    } else {
        report.is_valid = true;
        ss << "Конструкція надійна. Запас міцності: "
           << std::fixed << std::setprecision(1) << report.safety_factor
           << ". CAD-діаметр отвору під магніт: "
           << std::fixed << std::setprecision(2) << report.pocket.pocket_dia_cad_mm << " мм.";
    }

    report.notes = ss.str();
    return report;
}
