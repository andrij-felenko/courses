struct Config {
    std::size_t num_v{0};
    std::size_t num_c{0};
    std::vector<std::uint8_t> h_matrix;
    Algorithm algo{Algorithm::NormalizedMinSum};
    std::uint32_t max_iterations{50};
    float norm_factor{0.8f};
    float offset_factor{0.15f};
    float llr_clip_val{20.0f};
};
