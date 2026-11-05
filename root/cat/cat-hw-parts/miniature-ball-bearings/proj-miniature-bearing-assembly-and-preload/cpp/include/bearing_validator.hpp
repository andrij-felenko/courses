#pragma once

#include <string>
#include <string_view>

/**
 * @brief Геометричні параметри підшипника та початковий радіальний зазор
 */
struct BearingGeometry {
    std::string model;
    double inner_diameter_mm;    // Номінальний внутрішній діаметр d
    double outer_diameter_mm;    // Номінальний зовнішній діаметр D
    double width_mm;             // Ширина підшипника B
    double initial_clearance_um; // Початковий радіальний зазор (C0/CN), мкм
    double c0_stat_n;            // Статична вантажопідйомність C0, Н
};

/**
 * @brief Відхилення полів допусків для вала та корпусу (у мкм від номіналу)
 */
struct FitTolerance {
    double shaft_dev_min_um;
    double shaft_dev_max_um;
    double housing_dev_min_um;
    double housing_dev_max_um;
};

/**
 * @brief Звіт результатів розрахунку та валідації монтажного вузла
 */
struct ValidationReport {
    bool is_valid = false;
    double shaft_interference_max_um = 0.0;
    double housing_interference_max_um = 0.0;
    double clearance_reduction_um = 0.0;
    double residual_clearance_um = 0.0;
    double preload_recommended_min_n = 0.0;
    double preload_recommended_max_n = 0.0;
    std::string summary_message;
};

/**
 * @brief Клас перевірки посадок і розрахунку натягу підшипникового вузла
 */
class BearingAssemblyValidator {
public:
    explicit BearingAssemblyValidator(BearingGeometry geometry);

    [[nodiscard]] ValidationReport validate(const FitTolerance& fits) const;

private:
    BearingGeometry geometry_;

    [[nodiscard]] double compute_clearance_reduction(double shaft_fit_um, double housing_fit_um) const;
};
