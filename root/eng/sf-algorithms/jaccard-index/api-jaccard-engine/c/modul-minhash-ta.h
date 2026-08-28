typedef struct jaccard_minhash_engine jaccard_minhash_engine_t;

jaccard_status_t jaccard_minhash_engine_create(
    const jaccard_config_t *cfg,
    jaccard_minhash_engine_t **out_engine
);

jaccard_status_t jaccard_minhash_compute_sig(
    const jaccard_minhash_engine_t *engine,
    const jaccard_set_t *set_in,
    jaccard_signature_t *out_sig
);

jaccard_status_t jaccard_minhash_compare_sigs(
    const jaccard_signature_t *sig_a,
    const jaccard_signature_t *sig_b,
    double *out_similarity
);

void jaccard_minhash_engine_destroy(jaccard_minhash_engine_t *engine);
