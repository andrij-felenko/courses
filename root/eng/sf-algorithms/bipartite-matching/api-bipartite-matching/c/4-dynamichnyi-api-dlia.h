/* C API: Динамічне оновлення графа */
typedef struct DynamicMatchingState DynamicMatchingState;

DynamicMatchingState* dynamic_matching_create(int u_size, int v_size);
void dynamic_matching_destroy(DynamicMatchingState* state);

/* Додавання ребра з підтриманням поточного паросполучення за O(V + E) */
bool dynamic_matching_insert_edge(DynamicMatchingState* state, int u, int v);

/* Видалення ребра */
bool dynamic_matching_remove_edge(DynamicMatchingState* state, int u, int v);

int dynamic_matching_get_size(const DynamicMatchingState* state);
