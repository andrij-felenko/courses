#pragma once

#include <string>
#include <string_view>

/**
 * @brief Матеріал корпусної деталі, в яку встановлюється магніт
 */
enum class HousingMaterial {
    Aluminum6061,  /* Фрезерований алюміній (висока точність, без усадки) */
    PetgPrint,     /* 3D-друк PETG (помірна усадка ~0.8%, еластичний) */
    AbsPrint,      /* 3D-друк ABS (значна усадка ~1.5%, ризик розшарування) */
    MildSteel      /* Феромагнітна конструкційна сталь (замикає потік) */
};

/**
 * @brief Технічні характеристики неодимового магніту
 */
struct MagnetSpec {
    std::string grade;        /* Марка NdFeB (наприклад, "N42", "N52") */
    double diameter_mm = 0.0; /* Зовнішній діаметр D, мм */
    double thickness_mm = 0.0;/* Товщина h, мм */
    double br_tesla = 0.0;    /* Залишкова магнітна індукція Br, Тл */
};

/**
 * @brief Розрахункова геометрія посадкового гнізда під магніт
 */
struct PocketGeometry {
    double pocket_dia_cad_mm = 0.0;   /* Номінальний діаметр отвору в CAD-моделі */
    double pocket_depth_mm = 0.0;     /* Глибина гнізда під магніт */
    double effective_glue_gap_mm = 0.0;/* Фактичний радіальний зазор під клей */
    double glue_area_mm2 = 0.0;        /* Повна площа клейового з'єднання */
};

/**
 * @brief Звіт результатів розрахунку та валідації магнітного вузла
 */
struct LatchValidationReport {
    bool is_valid = false;
    double b_surface_tesla = 0.0;
    double pull_force_n = 0.0;
    double shear_stress_mpa = 0.0;
    double safety_factor = 0.0;
    PocketGeometry pocket;
    std::string notes;
};

/**
 * @brief Клас конфігуратора магнітного замка
 */
class MagneticLatchConfigurator {
public:
    MagneticLatchConfigurator(MagnetSpec magnet, HousingMaterial material);

    [[nodiscard]] LatchValidationReport validate(double target_glue_gap_mm,
                                                double adhesive_shear_limit_mpa,
                                                double air_gap_mm) const;

    [[nodiscard]] static std::string_view get_material_name(HousingMaterial material) noexcept;

private:
    MagnetSpec magnet_;
    HousingMaterial material_;

    [[nodiscard]] double compute_shrinkage_compensation() const noexcept;
    [[nodiscard]] double compute_flux_density(double gap_mm) const noexcept;
    [[nodiscard]] double compute_pull_force(double b_tesla) const noexcept;
};
