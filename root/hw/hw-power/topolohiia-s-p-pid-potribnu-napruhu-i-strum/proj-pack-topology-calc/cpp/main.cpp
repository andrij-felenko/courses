#include <iostream>
#include <cmath>
#include <string_view>
#include <expected>
#include <iomanip>

enum class BusbarMaterial {
    Copper,
    Nickel,
    NickelPlatedSteel
};

struct CellSpec {
    double v_nom{3.6};       // В
    double v_min{2.5};       // В
    double v_max{4.2};       // В
    double cap_ah{4.5};      // А·год
    double i_cont_max{15.0}; // А
    double i_peak_max{30.0}; // А
    double r_internal{0.018};// Ом (18 мОм)
    double weight_g{70.0};   // г
};

struct SystemRequirements {
    double v_target_nom{48.0};   // В
    double v_inverter_min{38.0}; // В
    double v_inverter_max{58.8}; // В
    double p_continuous_w{2500.0};// Вт
    double p_peak_w{5000.0};     // Вт
    double energy_wh_req{1200.0};// Вт·год
};

struct PackDesign {
    int s_count{0};
    int p_count{0};
    int total_cells{0};
    double v_pack_nom{0.0};
    double v_pack_min{0.0};
    double v_pack_max{0.0};
    double cap_pack_ah{0.0};
    double energy_pack_wh{0.0};
    double i_cont_max{0.0};
    double i_peak_max{0.0};
    double r_pack_total{0.0};
    double v_sag_continuous{0.0};
    double v_sag_peak{0.0};
    double busbar_area_mm2{0.0};
    double total_weight_kg{0.0};
};

enum class SizingError {
    VoltageOutOfRange,
    InvalidCellParameters,
    ZeroPowerRequested
};

constexpr double get_busbar_resistivity(BusbarMaterial mat) noexcept {
    switch (mat) {
        case BusbarMaterial::Copper: return 17.2;
        case BusbarMaterial::Nickel: return 96.0;
        case BusbarMaterial::NickelPlatedSteel: return 130.0;
    }
    return 17.2;
}

constexpr double get_target_current_density(BusbarMaterial mat) noexcept {
    switch (mat) {
        case BusbarMaterial::Copper: return 5.0; // А/мм²
        case BusbarMaterial::Nickel: return 1.5;
        case BusbarMaterial::NickelPlatedSteel: return 1.0;
    }
    return 5.0;
}

std::expected<PackDesign, SizingError> calculate_pack_topology(
    const CellSpec& cell,
    const SystemRequirements& req,
    BusbarMaterial busbar_mat = BusbarMaterial::Copper) noexcept 
{
    if (cell.v_nom <= 0.0 || cell.cap_ah <= 0.0 || cell.i_cont_max <= 0.0) {
        return std::unexpected(SizingError::InvalidCellParameters);
    }
    if (req.p_continuous_w <= 0.0 || req.v_target_nom <= 0.0) {
        return std::unexpected(SizingError::ZeroPowerRequested);
    }

    PackDesign design;

    // 1. Послідовні групи S
    design.s_count = static_cast<int>(std::ceil(req.v_target_nom / cell.v_nom));
    design.v_pack_nom = design.s_count * cell.v_nom;
    design.v_pack_min = design.s_count * cell.v_min;
    design.v_pack_max = design.s_count * cell.v_max;

    if (design.v_pack_max > req.v_inverter_max || design.v_pack_min < req.v_inverter_min) {
        return std::unexpected(SizingError::VoltageOutOfRange);
    }

    // 2. Струми навантаження
    const double i_cont_req = req.p_continuous_w / design.v_pack_min;
    const double i_peak_req = req.p_peak_w / design.v_pack_min;

    // 3. Паралельні банки P
    const int p_cont = static_cast<int>(std::ceil(i_cont_req / cell.i_cont_max));
    const int p_peak = static_cast<int>(std::ceil(i_peak_req / cell.i_peak_max));
    const int p_energy = static_cast<int>(std::ceil(req.energy_wh_req / (design.v_pack_nom * cell.cap_ah)));

    design.p_count = std::max({p_cont, p_peak, p_energy, 1});
    design.total_cells = design.s_count * design.p_count;

    // 4. Електричні параметри
    design.cap_pack_ah = design.p_count * cell.cap_ah;
    design.energy_pack_wh = design.v_pack_nom * design.cap_pack_ah;
    design.i_cont_max = design.p_count * cell.i_cont_max;
    design.i_peak_max = design.p_count * cell.i_peak_max;

    constexpr double r_interconnect_per_s = 0.0015; // 1.5 мОм на S-групу
    design.r_pack_total = design.s_count * ((cell.r_internal / design.p_count) + r_interconnect_per_s);

    // 5. Просадка напруги
    design.v_sag_continuous = i_cont_req * design.r_pack_total;
    design.v_sag_peak = i_peak_req * design.r_pack_total;

    // 6. Шина та маса
    const double j_target = get_target_current_density(busbar_mat);
    design.busbar_area_mm2 = i_cont_req / j_target;
    design.total_weight_kg = (design.total_cells * cell.weight_g) / 1000.0;

    return design;
}

int main() {
    constexpr CellSpec cell_21700{
        .v_nom = 3.6,
        .v_min = 2.5,
        .v_max = 4.2,
        .cap_ah = 4.5,
        .i_cont_max = 15.0,
        .i_peak_max = 30.0,
        .r_internal = 0.018,
        .weight_g = 70.0
    };

    constexpr SystemRequirements drone_req{
        .v_target_nom = 48.0,
        .v_inverter_min = 38.0,
        .v_inverter_max = 58.8,
        .p_continuous_w = 2500.0,
        .p_peak_w = 5000.0,
        .energy_wh_req = 1200.0
    };

    auto result = calculate_pack_topology(cell_21700, drone_req, BusbarMaterial::Copper);

    if (!result) {
        std::cerr << "Помилка розрахунку конфігурації батареї!\n";
        return 1;
    }

    const auto& d = *result;
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Звіт проєктування батареї (C++20) ===\n";
    std::cout << "Конфігурація: " << d.s_count << "S" << d.p_count << "P"
              << " (Всього банок: " << d.total_cells << ")\n";
    std::cout << "Напруга пакета: " << d.v_pack_nom << " В (Діапазон: "
              << d.v_pack_min << " В .. " << d.v_pack_max << " В)\n";
    std::cout << "Ємність: " << d.cap_pack_ah << " А·год | Енергія: " 
              << d.energy_pack_wh << " Вт·год\n";
    std::cout << "DCIR пакета: " << (d.r_pack_total * 1000.0) << " мОм\n";
    std::cout << "Просадка напруги: " << d.v_sag_continuous << " В (ном) / " 
              << d.v_sag_peak << " В (пік)\n";
    std::cout << "Переріз шини: " << d.busbar_area_mm2 << " мм²\n";
    std::cout << "Маса комірок: " << d.total_weight_kg << " кг\n";

    return 0;
}
