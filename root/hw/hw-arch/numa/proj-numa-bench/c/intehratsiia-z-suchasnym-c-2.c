// Використання в C: явна передача вузла при створенні структур даних
typedef struct {
    uint64_t *items;
    size_t count;
    int node;
} numa_vector_t;

numa_vector_t* numa_vector_create(size_t count, int node) {
    numa_vector_t *vec = (numa_vector_t*)malloc(sizeof(numa_vector_t));
    vec->count = count;
    vec->node = node;
    vec->items = (uint64_t*)numa_alloc_onnode(count * sizeof(uint64_t), node);
    return vec;
}

void numa_vector_destroy(numa_vector_t *vec) {
    if (vec) {
        numa_free(vec->items, vec->count * sizeof(uint64_t));
        free(vec);
    }
}
