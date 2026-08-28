#include <span>
#include <array>
#include <expected>
#include <vector>

namespace thermal {

class ThermalSolver {
public:
    ThermalSolver(SolverConfig config, MaterialProperties material);

    // Встановити граничні умови для 4 граней розрахункової області
    void set_boundary_conditions(const std::array<BoundaryCondition, 4>& bcs) noexcept;

    // Обчислити максимальний припустимий часовий крок за критерієм CFL
    [[nodiscard]] double max_stable_dt() const noexcept;

    // Запустити обчислення (повертає void або помилку SolverStatus)
    [[nodiscard]] std::expected<void, SolverStatus> run();

    // Отримати доступ до результатів розрахунку розподілу температури
    [[nodiscard]] std::span<const double> temperature_grid() const noexcept;

private:
    SolverConfig config_;
    MaterialProperties material_;
    std::array<BoundaryCondition, 4> bcs_;
    std::vector<double> grid_;
};

} // namespace thermal
