#include <cstddef>
#include <cstdint>

namespace thermal {

enum class BoundaryType : std::uint8_t {
    Dirichlet = 0, // Задана температура T_surface [°C]
    Neumann   = 1, // Заданий потік q_surface [Вт/м²]
    Robin     = 2, // Конвекція h * (T_s - T_amb)
    Radiation = 3  // Випромінювання ε * σ * (T_s⁴ - T_amb⁴)
};

enum class SolverStatus : std::int32_t {
    Success          =  0,
    NullPointer      = -1,
    InvalidParameter = -2,
    CflViolation     = -3,
    NoConvergence    = -4
};

struct MaterialProperties {
    double conductivity{385.0};    // k [Вт/(м·К)] (значення за замовчуванням для міді)
    double density{8960.0};        // ρ [кг/м³]
    double specific_heat{385.0};   // c_p [Дж/(кг·К)]
    double emissivity{0.05};       // ε (полірована мідна поверхня)

    // Обчислити коефіцієнт температуропровідності α = k / (ρ * c_p)
    [[nodiscard]] constexpr double diffusivity() const noexcept {
        return conductivity / (density * specific_heat);
    }
};

struct BoundaryCondition {
    BoundaryType type{BoundaryType::Dirichlet};
    double value{20.0};            // T [°C] або q [Вт/м²]
    double h_coeff{10.0};          // h [Вт/(м²·К)]
    double t_ambient{20.0};        // T_ambient [°C]
};

struct SolverConfig {
    std::size_t grid_x{100};
    std::size_t grid_y{100};
    double dx{0.001};              // 1 мм
    double dy{0.001};              // 1 мм
    double dt{0.0001};             // 0.1 мс
    double max_time{1.0};          // 1 секунда
    double tolerance{1e-6};
    bool is_transient{true};
};

} // namespace thermal
