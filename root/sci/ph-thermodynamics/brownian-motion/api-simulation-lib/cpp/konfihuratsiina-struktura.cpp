namespace brownian {

struct Config {
    double temperature{300.0};       // К
    double viscosity{1.002e-3};      // Па·с
    double particle_radius{1.0e-6};  // м
    double particle_mass{4.189e-15}; // кг
    double active_velocity{0.0};     // м/с
    double dt{1.0e-7};               // с
    std::size_t trajectory_steps{1000};
    std::size_t ensemble_size{500};
    unsigned int random_seed{0};
    SimMode mode{SimMode::ExactLangevin};
    int dimension{2};

    [[nodiscard]] double calculate_gamma() const noexcept {
        constexpr double pi = 3.14159265358979323846;
        return 6.0 * pi * viscosity * particle_radius;
    }

    [[nodiscard]] double calculate_theoretical_D() const noexcept {
        constexpr double kB = 1.380649e-23;
        return (kB * temperature) / calculate_gamma();
    }
};

} // namespace brownian
