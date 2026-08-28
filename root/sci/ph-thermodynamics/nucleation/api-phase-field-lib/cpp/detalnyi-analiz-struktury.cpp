namespace phasefield {

struct SolverConfig {
    std::size_t nx{128};
    std::size_t ny{128};
    double dx{1.0};
    double dt{0.01};
    double kappa{1.0};
    double mobility{1.0};
    bool use_openmp{true};
};

} // namespace phasefield
