#ifndef ELECTROSTATIC_ENERGY_CALCULATOR_HPP
#define ELECTROSTATIC_ENERGY_CALCULATOR_HPP

#include <vector>
#include <cstdint>
#include <system_error>
#include <expected>

namespace electrostatics {

struct GridPoint {
    std::uint32_t x;
    std::uint32_t y;
    std::uint32_t z;
};

enum class BoundaryType {
    Dirichlet,
    Neumann
};

struct ElectrodeSpec {
    std::uint16_t electrode_id;
    double potential_volts;
    BoundaryType boundary_type;
    std::vector<GridPoint> nodes;
};

struct GridConfig {
    std::uint32_t nx{100};
    std::uint32_t ny{100};
    std::uint32_t nz{1};
    double step_size_meters{1e-3};
    double relative_permittivity{1.0};
};

struct EnergyResult {
    double total_energy_joules{0.0};
    double max_energy_density_j_m3{0.0};
    double mean_energy_density_j_m3{0.0};
    std::uint32_t iterations_count{0};
    bool is_converged{false};
};

enum class ErrorCode {
    InvalidGridSize,
    InvalidStepSize,
    InvalidPermittivity,
    ElectrodeOutOfBounds,
    SolverDiverged
};

class ElectrostaticEnergyCalculator {
public:
    explicit ElectrostaticEnergyCalculator(const GridConfig& config);
    ~ElectrostaticEnergyCalculator() = default;

    // Скидання або зміна конфігурації сітки
    std::expected<void, ErrorCode> set_grid_config(const GridConfig& config);

    // Додавання електрода до розрахункової області
    std::expected<void, ErrorCode> add_electrode(const ElectrodeSpec& electrode);

    // Задання об'ємного заряду у вузлі
    std::expected<void, ErrorCode> set_charge_density(std::uint32_t x, std::uint32_t y, std::uint32_t z, double rho_c_m3);

    // Виконання чисельного розв'язку рівняння Пуассона
    std::expected<void, ErrorCode> solve_field(std::uint32_t max_iterations = 10000, double tolerance = 1e-7);

    // Обчислення повної енергії поля по об'єму
    [[nodiscard]] EnergyResult calculate_total_energy() const noexcept;

    // Отримання локального значення потенціалу у точці
    [[nodiscard]] double get_potential(std::uint32_t x, std::uint32_t y, std::uint32_t z) const;

    // Отримання вектора напруженості E у точці (Ex, Ey, Ez)
    [[nodiscard]] std::vector<double> get_electric_field(std::uint32_t x, std::uint32_t y, std::uint32_t z) const;

    // Аналітичний розрахунок для ідеального плоского конденсатора
    [[nodiscard]] static double analytical_flat_capacitor_energy(
        double area_sq_m, 
        double distance_m, 
        double voltage_volts, 
        double relative_permittivity = 1.0) noexcept;
};

} // namespace electrostatics

#endif // ELECTROSTATIC_ENERGY_CALCULATOR_HPP
