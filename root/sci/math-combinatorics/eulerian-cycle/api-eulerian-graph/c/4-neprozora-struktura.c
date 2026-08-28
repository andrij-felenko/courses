typedef struct euler_graph_s euler_graph_t;

struct euler_graph_s {
    int num_vertices;            /* Кількість вершин V */
    int num_edges;               /* Кількість ребер E */
    euler_graph_type_t type;     /* Тип графа */
    int* in_degree;              /* Масив вхідних степеней */
    int* out_degree;             /* Масив вихідних степеней */
    void* adj_lists;             /* Списки суміжності */
    bool is_frozen;              /* Прапорець заклинення */
};
