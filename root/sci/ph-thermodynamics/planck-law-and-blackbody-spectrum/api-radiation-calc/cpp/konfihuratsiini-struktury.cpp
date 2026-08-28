namespace blackbody {

/* Структура фізичних констант C++20 з constexpr значеннями */
struct Constants {
    static constexpr double h = 6.62607015e-34;
    static constexpr double c = 2.99792458e8;
    static constexpr double k_b = 1.380649e-23;
    static constexpr double sigma = 5.670374e-8;
    static constexpr double b_wien = 2.897771955e-3;
};

/* Налаштування чисельного інтегрування C++20 */
struct IntegrationConfig {
    std::size_t max_subintervals{5000};
    double rel_tolerance{1.0e-8};
    double abs_tolerance{1.0e-12};
    bool use_gauss_legendre{true};
};

/* Результат обчислення спектрального діапазону C++20 */
struct BandResult {
    double integrated_radiance{0.0};
    double integrated_emittance{0.0};
    double peak_wavelength{0.0};
    double estimated_error{0.0};
};

} // namespace blackbody
