/**
 * Перевіряє, чи є дана підмножина вершин великою та монохроматичною.
 */
ph_status_t ph_check_subset(
    const uint8_t *coloring,
    uint32_t n_nodes,
    uint64_t mask,
    const ph_config_t *config,
    bool *is_large_mono
);
