void run_full_pipeline_c(const double *signal, size_t n) {
    TakensConfig config;
    takens_config_init_default(&config);

    size_t opt_delay = 0;
    size_t opt_dim = 0;

    if (takens_compute_mutual_information(signal, n, &config, NULL, &opt_delay) != TAKENS_OK) return;
    if (takens_compute_fnn(signal, n, opt_delay, &config, NULL, &opt_dim) != TAKENS_OK) return;

    TakensEmbedding *emb = NULL;
    if (takens_embedding_create(signal, n, opt_delay, opt_dim, &emb) == TAKENS_OK) {
        printf("Успішно побудовано матрицю розміром %zu x %zu\n", emb->rows, emb->cols);
        
        /* Робота з даними emb->matrix_data ... */

        takens_embedding_free(emb); /* Обов'язкове звільнення пам'яті */
    }
}
