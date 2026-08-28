namespace ElectroDynamics {

class SurfaceChargeSolver {
public:
    // Конструктор ініціалізує сітку заданого розміру та виділяє пам'ять
    explicit SurfaceChargeSolver(const SolverConfig& config);

    // Деструктор автоматично звільняє внутрішні масиви сітки
    ~SurfaceChargeSolver() noexcept;

    // Заборона копіювання для запобігання важкому дублюванню масивів у пам'яті
    SurfaceChargeSolver(const SurfaceChargeSolver&) = delete;
    SurfaceChargeSolver& operator=(const SurfaceChargeSolver&) = delete;

    // Конструктор та оператор переміщення для передачі володіння об'єктом
    SurfaceChargeSolver(SurfaceChargeSolver&&) noexcept;
    SurfaceChargeSolver& operator=(SurfaceChargeSolver&&) noexcept;

    // Задання фізичних властивостей поодинокого вузла сітки
    [[nodiscard]] SolverStatus set_node(std::size_t ix, std::size_t iy, 
                                       BoundaryType type, double potential_v, 
                                       double conductivity_sm);

    // Заповнення прямокутної області провідним матеріалом з питомою провідністю σ
    [[nodiscard]] SolverStatus set_rectangular_conductor(std::size_t x0, std::size_t y0, 
                                                        std::size_t width, std::size_t height, 
                                                        double conductivity_sm);

    // Основний метод запуску чисельного розрахунку полів та поверхневих зарядів
    [[nodiscard]] SolverStatus compute();

    // Повернення неволодіючого зрізу std::span для безпечного читання всього масиву вузлів
    [[nodiscard]] std::span<const GridNode> get_mesh_data() const noexcept;

    // Отримання густини поверневого заряду σ_surf (Кл/м²) у конкретному граничному вузлі (ix, iy)
    [[nodiscard]] double get_surface_charge(std::size_t ix, std::size_t iy) const;

    // Розрахунок інтегрального потоку вектора Пойнтінга (Вт) крізь контрольний замкнений контур
    [[nodiscard]] double get_poynting_flux_watts(std::size_t start_x, std::size_t start_y, 
                                                std::size_t end_x, std::size_t end_y) const;

    // Експорт результатів розрахунку у файли CSV та VTK для візуалізації в ParaView
    [[nodiscard]] bool export_to_csv(const char* filepath) const noexcept;
    [[nodiscard]] bool export_to_vtk(const char* filepath) const noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace ElectroDynamics
