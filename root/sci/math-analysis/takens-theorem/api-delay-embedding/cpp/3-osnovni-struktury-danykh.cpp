namespace takens {
struct Config {
    size_t max_delay{50};
    size_t n_bins{32};
    size_t max_embedding_dim{10};
    double r_tol{15.0};
    double fnn_threshold{0.01};
    size_t num_threads{0};
};
}
