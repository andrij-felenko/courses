namespace latgeom {

struct SvpSolution {
    std::vector<int64_t> coordinates;
    std::vector<double> vector;
    double euclidean_norm{0.0};
    double hermite_factor{0.0};
    double root_hermite_factor{0.0};
    uint64_t visited_nodes{0};
    double execution_time_ms{0.0};
};

} // namespace latgeom
