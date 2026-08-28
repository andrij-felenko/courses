void run_fnn_example_cpp(const std::vector<double>& signal, size_t delay) {
    takens::Config config;
    config.max_embedding_dim = 8;
    config.r_tol = 15.0;

    auto result = takens::compute_fnn(signal, delay, config);
    if (result.has_value()) {
        std::cout << "Оптимальна вимірність m: " << result->optimal_dim << "\n";
    }
}
