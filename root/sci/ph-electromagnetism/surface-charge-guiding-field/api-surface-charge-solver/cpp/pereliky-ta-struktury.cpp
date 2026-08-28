namespace ElectroDynamics {

// Типи крайових умов у вузлах обчислювальної сітки
enum class BoundaryType : uint8_t {
    FreeSpace = 0,        // Вільний діелектрик (повітря, субстрат)
    ConductorBulk = 1,    // Внутрішній об'єм провідника (ρ = 0)
    DirichletFix = 2,    // Фіксований потенціал (електрод джерела V = const)
    NeumannFix = 3,      // Фіксований потік поля (∂V/∂n = const)
    InterfaceBoundary = 4 // Межа двох матеріалів із різною провідністю σ1 / σ2
};

// Метод чисельного інтегрування та розв'язання лінійних систем
enum class SolverEngine : uint8_t {
    SOR_Relaxation = 0,   // Послідовна верхня релаксація (Successive Over-Relaxation)
    ConjugateGradient = 1, // Метод спряжених градієнтів (Conjugate Gradient, CG)
    MultigridFDM = 2      // Багатосітковий метод (Multigrid FDM)
};

// Геометричні та фізичні параметри дискретного вузла сітки
struct alignas(16) GridNode {
    double x;              // Фізична координата X у метрах
    double y;              // Фізична координата Y у метрах
    double potential;      // Скалярний електричний потенціал V (Вольти)
    double conductivity;   // Питома електрична провідність σ (Сім/м)
    double charge_density; // Поверхнева густина заряду σ_surf (Кулон/м²)
    BoundaryType boundary; // Тип граничної умови у даному вузлі
};

// Повний набір налаштувань математичного ядра солівера
struct SolverConfig {
    std::size_t grid_nx{256};         // Кількість вузлів по осі X
    std::size_t grid_ny{256};         // Кількість вузлів по осі Y
    double mesh_step_m{1e-4};          // Крок сітки дискретизації h у метрах (0.1 мм)
    double relaxation_omega{1.85};     // Параметр релаксації ω (1.0 < ω < 2.0)
    double tolerance_volts{1e-7};      // Поріг збіжності за напругою (Вольти)
    std::size_t max_iters{10000};      // Максимально припустима кількість ітерацій
    SolverEngine engine{SolverEngine::SOR_Relaxation}; // Тип чисельного двигуна
    bool enable_poynting_calc{true};   // Розраховувати вектори B та Пойнтінга S
};

// Коди помилок та статуси виконання операцій
enum class SolverStatus : int32_t {
    Success = 0,            // Успішне виконання розрахунку
    InvalidGeometry = -1,   // Некоректна геометрія або незв'язана сітка
    DivergentSystem = -2,   // Чисельна розбіжність ітерацій (ω занадто велике)
    OutOfMemory = -3,       // Нестача оперативної пам'яті для масивів сітки
    Unconverged = -4        // Перевищено ліміт ітерацій max_iters без збіжності
};

} // namespace ElectroDynamics
