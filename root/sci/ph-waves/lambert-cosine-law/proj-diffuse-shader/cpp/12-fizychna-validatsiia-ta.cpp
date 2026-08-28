// Перевірка збереження енергії ламбертової BRDF методом Монте-Карло
bool validate_lambert_energy_conservation(const LambertShader& shader, double albedo_val, size_t sample_count = 100000) {
    CosineHemisphereSampler sampler;
    const Vec3 normal{0.0, 0.0, 1.0};
    const Vec3 light_pos{0.0, 0.0, 1.0}; // Нормальне падіння
    const ColorRGB light_power{1.0, 1.0, 1.0};

    double accumulated_energy = 0.0;

    for (size_t i = 0; i < sample_count; ++i) {
        const Vec3 dir = sampler.sample(normal);
        // Оскільки напрямки вже зважені за косинусом (pdf = cos θ / π),
        // інтеграл оцінюється як середня сума (BRDF * π)
        const ColorRGB color = shader.evaluate({0,0,0}, normal, dir, light_power);
        accumulated_energy += color.r * std::numbers::pi;
    }

    const double estimated_albedo = accumulated_energy / static_cast<double>(sample_count);
    const double error = std::abs(estimated_albedo - albedo_val);

    // Допускаємо похибку чисельного інтегрування Монте-Карло в межах 0.5%
    return error < 0.005;
}
