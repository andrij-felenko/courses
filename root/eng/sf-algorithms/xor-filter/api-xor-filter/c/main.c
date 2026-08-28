/* Коди результатів операцій C API */
typedef enum {
    XOR_OK = 0,
    XOR_ERR_NULL_POINTER = 1,
    XOR_ERR_EMPTY_INPUT = 2,
    XOR_ERR_ALLOCATION_FAILED = 3,
    XOR_ERR_MAX_ATTEMPTS_EXCEEDED = 4,
    XOR_ERR_INVALID_MAGIC = 5,
    XOR_ERR_UNSUPPORTED_VERSION = 6,
    XOR_ERR_BUFFER_TOO_SMALL = 7
} xor_error_t;

/* Структура 8-бітного фільтра */
typedef struct {
    uint64_t seed;          /* 64-бітний псевдовипадковий засів */
    uint32_t block_length;  /* Довжина сегмента L */
    uint8_t *fingerprints;  /* Масив слотів (3 * L) */
} xor_filter_8_t;
