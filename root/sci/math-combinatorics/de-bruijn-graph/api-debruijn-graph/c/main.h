#ifndef DEBRUIJN_API_H
#define DEBRUIJN_API_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок API */
typedef enum {
    DEBRUIJN_SUCCESS              =  0,
    DEBRUIJN_ERROR_INVALID_K      = -1,
    DEBRUIJN_ERROR_NOMEM          = -2,
    DEBRUIJN_ERROR_EMPTY_GRAPH    = -3,
    DEBRUIJN_ERROR_NOT_EULERIAN   = -4,
    DEBRUIJN_ERROR_INVALID_READ   = -5
} debruijn_status_t;

/* Типи бітового k-мера та ідентифікатора вершини */
typedef uint64_t kmer_t;
typedef uint64_t node_id_t;

/* Внутрішній вузол графа де Брейнена у компактному поданні */
typedef struct {
    kmer_t prefix_kmer;        /* Бітово-упакований (k-1)-мер вершини */
    uint8_t out_edges_mask;    /* Бітова маска вихідних ребер (4 біти для A, C, G, T) */
    uint8_t in_edges_mask;     /* Бітова маска вхідних ребер (4 біти для A, C, G, T) */
    uint32_t coverage;         /* Покриття (кількість знайдених повторів) */
} dbg_node_t;

/* Головний контекст графа */
typedef struct debruijn_graph_ctx debruijn_graph_ctx_t;

debruijn_graph_ctx_t* dbg_init(uint32_t k, size_t initial_capacity);
debruijn_status_t dbg_insert_read(debruijn_graph_ctx_t *ctx, const char *sequence, size_t seq_len);
size_t dbg_filter_low_coverage(debruijn_graph_ctx_t *ctx, uint32_t min_coverage);
debruijn_status_t dbg_compact_unitigs(debruijn_graph_ctx_t *ctx);
debruijn_status_t dbg_find_eulerian_path(debruijn_graph_ctx_t *ctx, char *out_buffer, size_t buffer_capacity, size_t *out_len);
void dbg_destroy(debruijn_graph_ctx_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* DEBRUIJN_API_H */
