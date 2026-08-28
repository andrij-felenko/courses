namespace gas_dynamics {

struct shock_wave_params {
    double upstream_mach{};       // Число Маха перед скачком M₁ (> 1.0)
    double downstream_mach{};     // Число Маха після скачка M₂ (< 1.0)
    double pressure_ratio{};      // Відношення статичних тисків p₂ / p₁
    double temperature_ratio{};   // Відношення статичних температур T₂ / T₁
    double density_ratio{};       // Відношення густин ρ₂ / ρ₁
    double total_pressure_loss{}; // Коефіцієнт збереження повного тиску p₀₂ / p₀₁
};

} // namespace gas_dynamics
