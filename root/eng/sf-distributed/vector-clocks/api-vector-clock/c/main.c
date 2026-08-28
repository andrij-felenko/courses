typedef uint64_t vc_counter_t;
typedef uint32_t vc_node_id_t;

/* Окремий запис версійного вектора для конкретного актора */
typedef struct {
    vc_node_id_t node_id;
    vc_counter_t counter;
    uint64_t physical_wall_time_ms; /* UTC мітка в мілісекундах для евристичного прибирання сміття */
} vc_entry_t;

/* Динамічний векторний годинник із підтримкою динамічного росту */
typedef struct {
    vc_entry_t *entries;
    size_t count;
    size_t capacity;
    bool is_sorted; /* оптимізаційний прапорець для бінарного пошуку O(log N) */
} vc_dynamic_clock_t;

/* Коди помилок бібліотеки */
typedef enum {
    VC_OK = 0,
    VC_ERR_NULL_PTR = -1,
    VC_ERR_OUT_OF_MEMORY = -2,
    VC_ERR_BUFFER_TOO_SMALL = -3,
    VC_ERR_CORRUPTED_DATA = -4,
    VC_ERR_NODE_NOT_FOUND = -5,
    VC_ERR_CAPACITY_EXCEEDED = -6,
    VC_ERR_COUNTER_OVERFLOW = -7
} vc_status_t;
