/* Функтор зі станом через контекстний покажчик у C */
typedef struct {
    const double *weights;
    size_t count;
} weight_context_t;

static inline size_t weight_min_op(size_t a, size_t b, const void *ctx) {
    const weight_context_t *w = (const weight_context_t *)ctx;
    return (w->weights[a] < w->weights[b]) ? a : b;
}
