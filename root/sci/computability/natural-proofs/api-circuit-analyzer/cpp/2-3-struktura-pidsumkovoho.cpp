namespace natural {
struct Result {
    uint64_t truth_table_size{0};
    uint64_t elapsed_time_us{0};
    double estimated_largeness{0.0};
    int max_walsh_transform{0};
    uint32_t algebraic_degree{0};
    bool is_constructive{false};
    bool is_large{false};
    bool is_useful_against_poly{false};
    bool is_natural{false};
};
}
