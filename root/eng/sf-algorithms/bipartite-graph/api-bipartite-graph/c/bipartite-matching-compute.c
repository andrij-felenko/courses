/* C API: Обчислення паросполучення обраним алгоритмом */
typedef enum {
    MATCHING_ALG_KUHN          = 0,  /* Алгоритм Куна DFS (O(|V|·|E|)) */
    MATCHING_ALG_HOPCROFT_KARP = 1   /* Алгоритм Гопкрофта-Карпа (O(|E|·√|V|)) */
} matching_algorithm_t;

bipartite_status_t bipartite_matching_compute(
    const bipartite_graph_t *graph,
    matching_algorithm_t algorithm,
    bipartite_matching_t *out_matching
);
