#include <cstdint>

namespace thermal {

// Фізичні константи
constexpr double STEFAN_BOLTZMANN = 5.670374419e-8; // σ [Вт/(м²·К⁴)]
constexpr double ABSOLUTE_ZERO_C  = -273.15;        // Абсолютний нуль [°C]

// Типи граничних умов
enum class BoundaryType : std::uint8_t {
    Dirichlet = 0, // 1-й рід: Задана температура T_surface [°C]
    Neumann   = 1, // 2-й рід: Заданий потік q_surface [Вт/м²]
    Robin     = 2, // 3-й рід: Конвекція h * (T_surface - T_ambient)
    Radiation = 3  // 4-й рід: Випромінювання ε * σ * (T_s⁴ - T_amb⁴)
};

// Статуси виконання функцій розв'язувача
enum class SolverStatus : std::int32_t {
    Success          =  0,
    NullPointer      = -1,
    InvalidParameter = -2,
    CflViolation     = -3,
    NoConvergence    = -4
};

} // namespace thermal
