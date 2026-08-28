#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Машинне слово довгої арифметики (лімб) */
typedef uint32_t bignum_limb_t;
typedef uint64_t bignum_dbl_limb_t;

/* Структура представлення беззнакового великого числа */
typedef struct {
    bignum_limb_t *limbs;  /* Масив лімбів у форматі little-endian */
    size_t length;         /* Кількість значущих лімбів */
    size_t capacity;       /* Загальна ємність виділеного буфера */
} bignum_t;

/* Коди повернення та помилок модуля */
typedef enum {
    BIGNUM_OK                  =  0,
    BIGNUM_ERR_NULL_POINTER    = -1,
    BIGNUM_ERR_BUFFER_OVERFLOW = -2,
    BIGNUM_ERR_INVALID_LENGTH  = -3,
    BIGNUM_ERR_OUT_OF_MEMORY   = -4
} bignum_status_t;

/* Параметри конфігурації алгоритму */
typedef struct {
    size_t karatsuba_threshold;  /* Поріг переходу на шкільний алгоритм (за замовчуванням 32) */
    size_t toom3_threshold;      /* Поріг переходу на Toom-3 (за замовчуванням 192) */
} bignum_config_t;
