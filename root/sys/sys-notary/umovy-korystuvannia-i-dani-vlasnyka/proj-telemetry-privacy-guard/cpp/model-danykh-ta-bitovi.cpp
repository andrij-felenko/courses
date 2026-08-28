enum class ConsentFlags : uint32_t {
    None             = 0,
    DiagnosticsBasic = 1U << 0, // Рівень 1: напруга, heap, лічильники збоїв
    PerformanceStats = 1U << 1, // Рівень 2: завантаження CPU, тривалість задач
    AnalyticsUsage   = 1U << 2, // Рівень 2: лічильники натискань, сесії
    LocationCoarse   = 1U << 3, // Рівень 2: огрублені координати (~1.1 км)
    LocationPrecise  = 1U << 4, // Рівень 3: точні супутникові координати GNSS
    NetworkTopology  = 1U << 5, // Рівень 3: Wi-Fi BSSID, IP-адреси мережі
    UserProfile      = 1U << 6  // Рівень 3: апаратний UID, серійний номер
};
