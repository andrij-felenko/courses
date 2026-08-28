typedef struct {
    uint32_t src;
    uint32_t dst;
} EdgeTuple;

/* Побудова CSR безпосередньо зі списку ребер за O(V + E) часу */
CsrGraph* csr_build_from_edge_list(uint32_t num_vertices, const EdgeTuple *edges, size_t num_edges) {
    CsrGraph *csr = (CsrGraph*)malloc(sizeof(CsrGraph));
    csr->num_vertices = num_vertices;
    csr->num_edges = num_edges;
    csr->offsets = (uint32_t*)calloc(num_vertices + 1, sizeof(uint32_t));
    csr->edges = (uint32_t*)malloc(num_edges * sizeof(uint32_t));

    /* 1. Підрахунок ступеня кожної вершини */
    for (size_t i = 0; i < num_edges; ++i) {
        if (edges[i].src < num_vertices) {
            csr->offsets[edges[i].src + 1]++;
        }
    }

    /* 2. Префіксна сума для обчислення початкових зміщень */
    for (uint32_t i = 0; i < num_vertices; ++i) {
        csr->offsets[i + 1] += csr->offsets[i];
    }

    /* Тимчасовий масив для відстеження поточного заповнення кожного зрізу */
    uint32_t *cursor = (uint32_t*)malloc(num_vertices * sizeof(uint32_t));
    for (uint32_t i = 0; i < num_vertices; ++i) {
        cursor[i] = csr->offsets[i];
    }

    /* 3. Розкладання кінців ребер у суцільний буфер edges */
    for (size_t i = 0; i < num_edges; ++i) {
        uint32_t u = edges[i].src;
        if (u < num_vertices) {
            csr->edges[cursor[u]++] = edges[i].dst;
        }
    }

    free(cursor);
    return csr;
}
