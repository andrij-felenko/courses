jaccard_status_t jaccard_compute_exact_sorted(
    const jaccard_set_t *set_a,
    const jaccard_set_t *set_b,
    double *out_similarity
);

bool jaccard_pass_size_filter(
    size_t len_a,
    size_t len_b,
    double threshold
);
