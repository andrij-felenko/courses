/**
 * Обчислює компоненти сильної зв'язаності орієнтованого графа за алгоритмом Таржана.
 *
 * @param num_vertices Загальна кількість вершин (пронумеровані 0..num_vertices-1).
 * @param adj_list Масив списків суміжності (adj_list[u] є масивом сусідів вершини u).
 * @param adj_sizes Масив вихідних ступенів вершин (adj_sizes[u] — довжина adj_list[u]).
 * @param config Показчик на структуру конфігурації (або NULL для замовчуваних значень).
 * @return Вказівник на виділену структуру SCCResult. Пам'ять звільняється через scc_free_result().
 */
SCCResult* scc_compute(
    int num_vertices,
    const int** adj_list,
    const int* adj_sizes,
    const SCCConfig* config
);

/**
 * Будує орієнтований ациклічний граф конденсації G^SCC.
 * Автоматично усуває дубльовані мета-ребра між однаковими компонентами.
 *
 * @param original_num_vertices Кількість вершин вихідного графа.
 * @param adj_list Список суміжності вихідного графа.
 * @param adj_sizes Вихідні ступені вершин вихідного графа.
 * @param result Результат виконання scc_compute().
 * @return Вказівник на структуру CondensationGraph. Пам'ять звільняється через scc_free_condensation().
 */
CondensationGraph* scc_build_condensation(
    int original_num_vertices,
    const int** adj_list,
    const int* adj_sizes,
    const SCCResult* result
);

/**
 * Експортує граф конденсації в текстовий формат Graphviz DOT для візуалізації.
 *
 * @param dag Вказівник на граф конденсації.
 * @param filename Шлях до вихідного DOT-файлу.
 * @return 0 при успіху, від'ємний код помилки при збої запису.
 */
int scc_export_dot(const CondensationGraph* dag, const char* filename);

/**
 * Безпечно звільняє пам'ять, виділену під структуру SCCResult.
 */
void scc_free_result(SCCResult* result);

/**
 * Безпечно звільняє пам'ять, виділену під структуру CondensationGraph.
 */
void scc_free_condensation(CondensationGraph* dag);
