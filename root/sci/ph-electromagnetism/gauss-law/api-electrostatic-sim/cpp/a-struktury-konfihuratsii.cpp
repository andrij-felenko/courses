// C++20 Grid Specifications
namespace physics::electrodynamics {

enum class BoundaryType {
    Dirichlet,
    Neumann,
    Robin
};

struct BoundaryCondition {
    BoundaryType type{BoundaryType::Dirichlet};
    double potential_volts{0.0};
    double normal_derivative{0.0};
};

struct GridConfig {
    size_t nx{32};
    size_t ny{32};
    size_t nz{32};
    double dx{0.01};
    double dy{0.01};
    double dz{0.01};
    BoundaryCondition boundary_x_min{};
    BoundaryCondition boundary_x_max{};
    BoundaryCondition boundary_y_min{};
    BoundaryCondition boundary_y_max{};
    BoundaryCondition boundary_z_min{};
    BoundaryCondition boundary_z_max{};
};

} // namespace physics::electrodynamics
