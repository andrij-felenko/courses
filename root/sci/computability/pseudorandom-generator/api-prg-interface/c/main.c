typedef struct {
    double prob_prg;      /* Імовірність Pr[D(G(s)) = 1] */
    double prob_random;   /* Імовірність Pr[D(r) = 1] */
    double advantage;     /* Перевага |prob_prg - prob_random| */
    size_t total_samples; /* Кількість випробувань */
} nw_test_result_t;

nw_status_t nw_evaluate_distinguisher(
    const nw_generator_ctx_t *ctx,
    const nw_distinguisher_t *distinguisher,
    size_t num_samples,
    nw_test_result_t *result
);
