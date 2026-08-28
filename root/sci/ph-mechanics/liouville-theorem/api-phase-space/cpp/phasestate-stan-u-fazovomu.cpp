struct PhaseState {
    std::size_t dim{0};
    std::vector<double> q{};
    std::vector<double> p{};
    double t{0.0};

    [[nodiscard]] double phase_norm() const noexcept {
        double sum = 0.0;
        for (std::size_t i = 0; i < dim; ++i) {
            sum += q[i] * q[i] + p[i] * p[i];
        }
        return std::sqrt(sum);
    }
};
