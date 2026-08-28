typedef struct PlanarGraph {
    int num_vertices;       /* Кількість вершин V */
    int num_edges;          /* Кількість ненапрямлених ребер E */
    int num_faces;          /* Кількість граней F */
    
    int* head;              /* Індекси перших напівребер для кожної вершини */
    HalfEdge* half_edges;   /* Масив напівребер розміром 2 * max_edges */
    int half_edge_count;    /* Поточна кількість напівребер у масиві */
    int max_edges;          /* Максимальна виділена місткість ребер */
    
    int** rotation_system;  /* rotation_system[u] — циклічний масив ребер навколо u */
    int* rotation_degree;   /* Ступінь кожної вершини deg(u) */
    bool is_embedded;       /* true, якщо вкладення побудовано успішно */
    
    PlanarFace* faces;      /* Масив топологічних граней розбиття */
} PlanarGraph;
