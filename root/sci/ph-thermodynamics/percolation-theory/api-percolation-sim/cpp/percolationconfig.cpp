struct PercolationConfig {
    uint32_t dim_x {100};            // Розмір ґратки вздовж осі X
    uint32_t dim_y {100};            // Розмір ґратки вздовж осі Y
    uint32_t dim_z {1};              // Розмір ґратки вздовж осі Z (1 для 2D)
    
    LatticeTopology topology {LatticeTopology::SQUARE_2D};
    PercolationMode mode {PercolationMode::SITE_PERCOLATION};
    BoundaryCondition boundary {BoundaryCondition::FREE_BOUNDARIES};
    
    double p_occupancy {0.5};        // Ймовірність відкриття вузла/зв'язку (p)
    uint64_t random_seed {0};        // Зародиш ГПСЧ (0 - випадковий системний запуск)
    uint32_t bethe_z {3};            // Координаційне число (лише для BETHE_TREE)
    
    bool compute_backbone {false};   // Обчислювати кістяк (backbone) кластера
    bool compute_fractal_dim {false};// Оцінювати фрактальну розмірність
};
