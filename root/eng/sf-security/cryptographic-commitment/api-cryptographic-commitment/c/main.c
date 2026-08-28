/* Контекст параметрів циклічної групи еліптичної кривої (наприклад, secp256k1 або ed25519) */
typedef struct pedersen_context_s pedersen_context_t;

/* Структура 256-бітного елемента поля або скаляра (BigEndian) */
typedef struct {
    uint8_t bytes[32];
} pedersen_scalar_t;

/* Структура 33-бітного стиснутого елемента групи / точки кривої */
typedef struct {
    uint8_t bytes[33];
} pedersen_point_t;

/* Коди помилок API */
typedef enum {
    PEDERSEN_SUCCESS = 0,
    PEDERSEN_ERROR_INVALID_PARAM = -1,
    PEDERSEN_ERROR_VERIFICATION_FAILED = -2,
    PEDERSEN_ERROR_RNG_FAILED = -3,
    PEDERSEN_ERROR_BUFFER_TOO_SMALL = -4
} pedersen_error_t;
