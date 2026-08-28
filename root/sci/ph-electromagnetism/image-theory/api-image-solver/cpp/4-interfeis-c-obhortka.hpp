namespace libesimage {

class ElectrostaticSolver {
public:
    explicit ElectrostaticSolver(const SolverConfig& config = {});
    ~ElectrostaticSolver();

    // Заборона копіювання (RAII)
    ElectrostaticSolver(const ElectrostaticSolver&) = delete;
    ElectrostaticSolver& operator=(const ElectrostaticSolver&) = delete;

    // Дозвіл переміщення
    ElectrostaticSolver(ElectrostaticSolver&&) noexcept;
    ElectrostaticSolver& operator=(ElectrostaticSolver&&) noexcept;

    uint32_t add_charge(const Vector3D& position, double charge_val);
    void set_geometry(const SolverConfig& config);

    [[nodiscard]] double get_potential(const Vector3D& point) const;
    [[nodiscard]] Vector3D get_field(const Vector3D& point) const;
    [[nodiscard]] Vector3D get_force(uint32_t charge_id) const;
    [[nodiscard]] double get_surface_charge_density(const Vector3D& point) const;

    [[nodiscard]] std::span<const PointCharge> get_image_charges() const noexcept;

private:
    es_solver_t* m_handle{nullptr};
};

} // namespace libesimage
