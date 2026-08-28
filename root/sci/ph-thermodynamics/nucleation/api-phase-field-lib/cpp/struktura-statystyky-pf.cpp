namespace phasefield {

struct SolverStats {
    std::uint64_t total_steps{0};
    double total_free_energy{0.0};
    double max_c_change{0.0};
    double execution_time_ms{0.0};
};

} // namespace phasefield
