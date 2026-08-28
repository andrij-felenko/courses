namespace percolate {

class PercolationEngine {
public:
    // Конструктор: ініціалізація структури ґратки та буферів
    explicit PercolationEngine(const PercolationConfig& config);
    ~PercolationEngine();

    // Заборона копіювання (RAII управління ресурсами)
    PercolationEngine(const PercolationEngine&) = delete;
    PercolationEngine& operator=(const PercolationEngine&) = delete;

    // Скидання стану ґратки та згенерованого шуму
    PercolationStatus reset();

    // Генерація випадкового стану ґратки для заданого p
    PercolationStatus generate_lattice(double p_override = -1.0);

    // Запуск алгоритму Гошена — Копельмана та обчислення статистики
    PercolationStatus analyze(ClusterAnalysisResult& out_result);

    // Експорт карти кластерів у двовимірний масив (або файл)
    PercolationStatus export_cluster_map(int32_t* out_buffer, size_t buffer_size) const;

    // Експорт структури у форматі VTK для візуалізації в ParaView
    PercolationStatus export_vtk(const std::string& filename) const;
};

// Запуск паралельного сканування Монте-Карло для пошуку критичного порогу p_c
PercolationStatus run_monte_carlo_sweep(
    const PercolationConfig& base_config,
    const MonteCarloSweepConfig& sweep_config,
    std::vector<ClusterAnalysisResult>& out_sweep_data
);

// Оцінка критичного порогу p_c методом бісекції
double estimate_critical_threshold(
    PercolationConfig base_config,
    double tolerance = 1e-4,
    uint32_t mc_samples = 5000
);

} // namespace percolate
