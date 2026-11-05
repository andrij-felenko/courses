#ifndef ORGANIZER_MATRIX_HPP
#define ORGANIZER_MATRIX_HPP

#include <string>
#include <vector>
#include <cmath>
#include <string_view>

namespace organizer {

// Базовий крок відкритого стандарту Gridfinity (мм)
inline constexpr double kGridfinityPitchMm = 42.0;

// Граничний нормативний час стікання статичного заряду за IEC 61340-5-1 (секунди)
inline constexpr double kEsdMaxDecayTimeSec = 2.0;

// Ряд номіналів компонентів
enum class ESeries {
    E12,
    E24
};

// Параметри деталі, що зберігається
struct PartInfo {
    std::string name;
    double length_mm{0.0};
    double width_mm{0.0};
    double height_mm{0.0};
    size_t count{0};

    [[nodiscard]] double unit_volume_mm3() const noexcept {
        return length_mm * width_mm * height_mm;
    }
};

// Одинична комірка органайзера
class StorageCell {
public:
    StorageCell(std::string label, double width_mm, double length_mm, double depth_mm);

    void assign_part(const PartInfo& part, double packing_density = 0.58, double safety_margin = 1.25);

    [[nodiscard]] const std::string& label() const noexcept { return label_; }
    [[nodiscard]] double width() const noexcept { return width_mm_; }
    [[nodiscard]] double length() const noexcept { return length_mm_; }
    [[nodiscard]] double depth() const noexcept { return depth_mm_; }
    [[nodiscard]] double capacity_volume_mm3() const noexcept { return width_mm_ * length_mm_ * depth_mm_; }
    [[nodiscard]] double required_volume_mm3() const noexcept { return required_volume_mm3_; }
    [[nodiscard]] bool is_overfilled() const noexcept;
    [[nodiscard]] double fill_percentage() const noexcept;

private:
    std::string label_;
    double width_mm_{0.0};
    double length_mm_{0.0};
    double depth_mm_{0.0};
    double required_volume_mm3_{0.0};
};

// Профіль електростатичної безпеки матеріалу
class EsdProfile {
public:
    explicit EsdProfile(double surface_resistivity_ohm_sq, double capacitance_pf = 100.0);

    // Розрахунок часу стікання заряду від V0 до V_target
    [[nodiscard]] double calculate_decay_time(double v_initial, double v_target) const noexcept;

    // Перевірка відповідності нормам IEC 61340-5-1 (спад заряду до 10% за час <= 2.0 с)
    [[nodiscard]] bool is_compliant(double v_initial = 1000.0, double v_target = 100.0) const noexcept;

    [[nodiscard]] double surface_resistivity() const noexcept { return surface_resistivity_; }

private:
    double surface_resistivity_{1.0e8};
    double capacitance_pf_{100.0};
};

// Модульна матриця касетного блоку
class OrganizerMatrix {
public:
    OrganizerMatrix(ESeries series, double cell_width_mm, double cell_length_mm, double cell_depth_mm, double wall_thickness_mm = 1.6);

    void generate_grid();
    bool set_part(size_t col, size_t row, const PartInfo& part);

    [[nodiscard]] size_t columns() const noexcept { return columns_; }
    [[nodiscard]] size_t rows() const noexcept { return rows_; }
    [[nodiscard]] double total_width_mm() const noexcept;
    [[nodiscard]] double total_length_mm() const noexcept;
    [[nodiscard]] const std::vector<StorageCell>& cells() const noexcept { return cells_; }

private:
    ESeries series_;
    size_t total_cells_{12};
    size_t columns_{4};
    size_t rows_{3};
    double cell_width_{0.0};
    double cell_length_{0.0};
    double cell_depth_{0.0};
    double wall_thickness_{1.6};
    std::vector<StorageCell> cells_;
};

} // namespace organizer

#endif // ORGANIZER_MATRIX_HPP
