/* Створення та знищення графа */
matching_graph_t* matching_graph_create(size_t num_vertices, matching_mode_t mode, const matching_allocator_t* alloc);
void matching_graph_destroy(matching_graph_t* graph);

/* Додавання ребра та аналіз складності */
matching_error_t matching_graph_add_edge(matching_graph_t* graph, int u, int v, double weight);

/* Обчислення паросполучення та звільнення пам'яті результату */
matching_error_t matching_solve(matching_graph_t* graph, matching_result_t* out_result, matching_stats_t* out_stats);
void matching_result_free(matching_result_t* result);
