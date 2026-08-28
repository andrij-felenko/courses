typedef enum {
    MATCHING_SUCCESS = 0,
    MATCHING_ERROR_INVALID_PARAM = -1,
    MATCHING_ERROR_OUT_OF_MEMORY = -2,
    MATCHING_ERROR_INDEX_OUT_OF_BOUNDS = -3,
    MATCHING_ERROR_GRAPH_TOO_LARGE = -4,
    MATCHING_ERROR_STATE_CORRUPTED = -5,
    MATCHING_ERROR_NULL_POINTER = -6
} matching_error_t;

typedef enum {
    MATCHING_MODE_CARDINALITY = 0,
    MATCHING_MODE_WEIGHTED_EXACT = 1,
    MATCHING_MODE_WEIGHTED_APPROX = 2
} matching_mode_t;

typedef struct {
    void* (*custom_malloc)(size_t size);
    void (*custom_free)(void* ptr);
    void* (*custom_realloc)(void* ptr, size_t new_size);
} matching_allocator_t;
