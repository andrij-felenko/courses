/* C API: Повертані коди помилок та статусів виконання */
typedef enum {
    BIPARTITE_SUCCESS          =  0,  /* Успішне обчислення */
    BIPARTITE_ERR_NULL_POINTER = -1,  /* Передано нульовий вказівник */
    BIPARTITE_ERR_INVALID_INDEX= -2,  /* Індекс вершини вийшов за межі [0, N-1] або [0, M-1] */
    BIPARTITE_ERR_OUT_OF_MEMORY= -3,  /* Не вдалося виділити пам'ять */
    BIPARTITE_ERR_INVALID_GRAPH= -4   /* Граф містить некоректні ребра або порушено дводольність */
} BipartiteStatus;

/* Конфігурація розв'язувача */
typedef enum {
    ALGORITHM_KUHN          = 0,  /* Простий DFS, O(V * E), оптимальний для малих і розріджених графів */
    ALGORITHM_HOPCROFT_KARP = 1,  /* Фазовий BFS+DFS, O(E * sqrt(V)), для великих графів */
    ALGORITHM_DINIC_FLOW    = 2   /* Зведення до потоку через алгоритм Дініца, O(E * sqrt(V)) */
} BipartiteAlgorithm;

/* Структура результату обчислення у C */
typedef struct {
    int matching_size;        /* Кількість ребер у максимальному паросполученні */
    int* match_u;             /* Масив розміром u_size: match_u[u] = v або -1 */
    int* match_v;             /* Масив розміром v_size: match_v[v] = u або -1 */
    int* vertex_cover_u;      /* Прапорець 0/1: чи належить u_i до мінімального покриття */
    int* vertex_cover_v;      /* Прапорець 0/1: чи належить v_j до мінімального покриття */
    double execution_time_ms; /* Час виконання у мілісекундах */
} MatchingResult;

/* Сигнатури функцій C API */
BipartiteStatus bipartite_graph_create(int u_size, int v_size, int initial_capacity, void** graph_handle);
void bipartite_graph_destroy(void* graph_handle);
BipartiteStatus bipartite_graph_add_edge(void* graph_handle, int u, int v);
BipartiteStatus bipartite_solve_matching(void* graph_handle, BipartiteAlgorithm algo, MatchingResult* result);
void bipartite_result_free(MatchingResult* result);
