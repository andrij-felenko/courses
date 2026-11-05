#include "organizer_matrix.hpp"
#include <stdexcept>
#include <iomanip>
#include <sstream>

namespace organizer {

StorageCell::StorageCell(std::string label, double width_mm, double length_mm, double depth_mm)
    : label_(std::move(label)), width_mm_(width_mm), length_mm_(length_mm), depth_mm_(depth_mm) {}

void StorageCell::assign_part(const PartInfo& part, double packing_density, double safety_margin) {
    if (packing_density <= 0.05 || packing_density > 1.0) {
        packing_density = 0.58; // Коефіцієнт насипного пакування циліндричних та призматичних тіл
    }
    if (safety_margin < 1.0) {
        safety_margin = 1.25; // 25% технологічного запасу для легкого виймання деталей пальцями
    }
    double pure_volume = part.unit_volume_mm3() * static_cast<double>(part.count);
    double bulk_volume = pure_volume / packing_density;
    required_volume_mm3_ = bulk_volume * safety_margin;
}

bool StorageCell::is_overfilled() const noexcept {
    return required_volume_mm3_ > capacity_volume_mm3();
}

double StorageCell::fill_percentage() const noexcept {
    double cap = capacity_volume_mm3();
    if (cap <= 0.0) return 0.0;
    return (required_volume_mm3_ / cap) * 100.0;
}

EsdProfile::EsdProfile(double surface_resistivity_ohm_sq, double capacitance_pf)
    : surface_resistivity_(surface_resistivity_ohm_sq), capacitance_pf_(capacitance_pf) {}

double EsdProfile::calculate_decay_time(double v_initial, double v_target) const noexcept {
    if (v_initial <= 0.0 || v_target <= 0.0 || v_initial <= v_target) {
        return 0.0;
    }
    // Ємність у Фарадах
    double c_farads = capacitance_pf_ * 1.0e-12;
    // Опір витоку пропорційний питомому поверхневому опору матеріалу
    double r_discharge = surface_resistivity_;
    double tau = r_discharge * c_farads;

    // Експоненційний закон спаду заряду: V(t) = V0 * exp(-t / tau)
    return -tau * std::log(v_target / v_initial);
}

bool EsdProfile::is_compliant(double v_initial, double v_target) const noexcept {
    double time = calculate_decay_time(v_initial, v_target);
    bool in_dissipative_range = (surface_resistivity_ >= 1.0e5 && surface_resistivity_ <= 1.0e11);
    return in_dissipative_range && (time <= kEsdMaxDecayTimeSec);
}

OrganizerMatrix::OrganizerMatrix(ESeries series, double cell_width_mm, double cell_length_mm, double cell_depth_mm, double wall_thickness_mm)
    : series_(series), cell_width_(cell_width_mm), cell_length_(cell_length_mm), cell_depth_(cell_depth_mm), wall_thickness_(wall_thickness_mm) {
    total_cells_ = (series_ == ESeries::E12) ? 12 : 24;
    generate_grid();
}

void OrganizerMatrix::generate_grid() {
    // Оптимізація конфігурації колонок та рядків до пропорції робочого столу 4:3
    size_t best_cols = total_cells_;
    size_t best_rows = 1;
    double min_diff = 1e9;

    for (size_t c = 1; c <= total_cells_; ++c) {
        if (total_cells_ % c == 0) {
            size_t r = total_cells_ / c;
            double w = static_cast<double>(c) * cell_width_ + static_cast<double>(c + 1) * wall_thickness_;
            double l = static_cast<double>(r) * cell_length_ + static_cast<double>(r + 1) * wall_thickness_;
            double ratio = w / l;
            double diff = std::abs(ratio - 1.333);
            if (diff < min_diff) {
                min_diff = diff;
                best_cols = c;
                best_rows = r;
            }
        }
    }
    columns_ = best_cols;
    rows_ = best_rows;

    cells_.clear();
    cells_.reserve(total_cells_);

    for (size_t r = 0; r < rows_; ++r) {
        char row_char = static_cast<char>('A' + r);
        for (size_t c = 0; c < columns_; ++c) {
            std::ostringstream ss;
            ss << row_char << (c + 1);
            cells_.emplace_back(ss.str(), cell_width_, cell_length_, cell_depth_);
        }
    }
}

bool OrganizerMatrix::set_part(size_t col, size_t row, const PartInfo& part) {
    if (col >= columns_ || row >= rows_) {
        return false;
    }
    size_t index = row * columns_ + col;
    cells_[index].assign_part(part);
    return true;
}

double OrganizerMatrix::total_width_mm() const noexcept {
    return static_cast<double>(columns_) * cell_width_ + static_cast<double>(columns_ + 1) * wall_thickness_;
}

double OrganizerMatrix::total_length_mm() const noexcept {
    return static_cast<double>(rows_) * cell_length_ + static_cast<double>(rows_ + 1) * wall_thickness_;
}

} // namespace organizer
