/* Конструктор та деструктор графа */
AdjMatrix* adj_matrix_create(size_t vertices);
void       adj_matrix_free(AdjMatrix* graph);

/* Основні модифікатори та селектори */
bool   adj_matrix_add_edge(AdjMatrix* g, size_t u, size_t v, double weight);
bool   adj_matrix_remove_edge(AdjMatrix* g, size_t u, size_t v);
bool   adj_matrix_has_edge(const AdjMatrix* g, size_t u, size_t v);
double adj_matrix_get_weight(const AdjMatrix* g, size_t u, size_t v);

/* Аналітичні та алгоритмічні операції */
size_t adj_matrix_out_degree(const AdjMatrix* g, size_t u);
size_t adj_matrix_in_degree(const AdjMatrix* g, size_t v);
bool   adj_matrix_floyd_warshall(const AdjMatrix* g, double* out_dist);
