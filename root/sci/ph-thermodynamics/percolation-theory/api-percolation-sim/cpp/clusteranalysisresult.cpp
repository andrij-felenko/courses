struct ClusterAnalysisResult {
    double occupied_fraction;        // Фактична частка відкритих вузлів
    uint32_t total_clusters;         // Загальна кількість кластерів
    uint32_t max_cluster_size;       // Розмір найбільшого кластера (вузлів)
    double p_infinite;               // Потужність протікаючого кластера P_∞(p)
    double mean_cluster_size_chi;    // Середній розмір скінченного кластера χ(p)
    
    bool has_spanning_x;             // Наявність протікання по осі X
    bool has_spanning_y;             // Наявність протікання по осі Y
    bool has_spanning_z;             // Наявність протікання по осі Z
    
    uint32_t backbone_site_count;    // Кількість вузлів, що ведуть струм (Backbone)
    double estimated_fractal_dim;    // Оцінка фрактальної розмірності d_f
    
    std::vector<uint32_t> cluster_size_distribution; // Масив n_s(p)
};
