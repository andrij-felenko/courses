typedef struct {
    int u;
    int v;
    double weight;
} matching_edge_t;

typedef struct {
    size_t num_edges;
    double total_weight;
    matching_edge_t* edges;
    int* mate_array;
} matching_result_t;

typedef struct {
    uint64_t num_augmentations;
    uint64_t num_blossoms_contracted;
    uint64_t num_lca_searches;
    double elapsed_milliseconds;
} matching_stats_t;
