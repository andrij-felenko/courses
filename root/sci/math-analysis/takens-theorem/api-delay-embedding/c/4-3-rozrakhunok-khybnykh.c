void run_fnn_example(const double *signal, size_t n, size_t delay) {
    TakensConfig config;
    takens_config_init_default(&config);
    config.max_embedding_dim = 8;
    config.r_tol = 15.0;

    double fnn_buffer[8];
    size_t opt_dim = 0;

    TakensStatus status = takens_compute_fnn(signal, n, delay, &config, fnn_buffer, &opt_dim);
    if (status == TAKENS_OK) {
        printf("Оптимальна вимірність m: %zu\n", opt_dim);
    }
}
