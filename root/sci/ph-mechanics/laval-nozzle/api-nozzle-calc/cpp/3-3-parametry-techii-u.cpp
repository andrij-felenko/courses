struct FlowPointState {
    double x{0.0};           // Осьова координата точки, м
    double area{0.0};        // Поперечна площа перерізу, м²
    double mach{0.0};        // Число Маха M
    double pressure{0.0};    // Статичний тиск P, Па
    double temp{0.0};        // Статична температура T, К
    double density{0.0};     // Густина ρ, кг/м³
    double vel{0.0};         // Швидкість газу u, м/с
    double P0_local{0.0};    // Локальний повний тиск P0, Па
};
