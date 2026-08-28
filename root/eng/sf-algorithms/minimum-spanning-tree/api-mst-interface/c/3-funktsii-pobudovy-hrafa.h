/* Непрозорий дескриптор графа */
typedef struct MstGraph MstGraph;

/* Створення графа з фіксованою кількістю вершин */
MstGraph* mst_graph_create(size_t num_vertices);

/* Додавання неорієнтованого ребра до графа */
MstStatusCode mst_graph_add_edge(MstGraph *graph, int32_t u, int32_t v, int64_t weight);

/* Пакетне додавання масиву ребер */
MstStatusCode mst_graph_add_edges_batch(MstGraph *graph, const MstEdgeDesc *edges, size_t count);

/* Отримання кількості вершин */
size_t mst_graph_get_vertex_count(const MstGraph *graph);

/* Звільнення всієї виділеної пам'яті графа */
void mst_graph_destroy(MstGraph *graph);
