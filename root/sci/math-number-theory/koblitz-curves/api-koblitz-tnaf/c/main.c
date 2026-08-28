#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define KOBLITZ_MAX_WORDS 9
#define KOBLITZ_MAX_TNAF_DIGITS 600

/* Статусні коди помилок */
typedef enum {
    KOBLITZ_OK                     = 0,
    KOBLITZ_ERR_NULL_PARAM         = -1,
    KOBLITZ_ERR_INVALID_CURVE      = -2,
    KOBLITZ_ERR_POINT_NOT_ON_CURVE = -3,
    KOBLITZ_ERR_POINT_AT_INFINITY  = -4,
    KOBLITZ_ERR_SCALAR_OUT_OF_RANGE= -5,
    KOBLITZ_ERR_BUFFER_TOO_SMALL   = -6,
    KOBLITZ_ERR_DIV_BY_ZERO        = -7,
    KOBLITZ_ERR_SELF_TEST_FAILED   = -8
} koblitz_status_t;

/* Елемент скінченного поля F_{2^m} */
typedef struct {
    uint64_t words[KOBLITZ_MAX_WORDS];
} koblitz_fe_t;

/* Точка кривої в афінних координатах: (x, y) */
typedef struct {
    koblitz_fe_t x;
    koblitz_fe_t y;
    bool is_infinity;
} koblitz_affine_point_t;

/* Точка кривої в проективних координатах Лопеса-Дахаба: (X : Y : Z) */
typedef struct {
    koblitz_fe_t X;
    koblitz_fe_t Y;
    koblitz_fe_t Z;
    bool is_infinity;
} koblitz_proj_point_t;

/* Алгебраїчне число в кільці Z[tau]: rho = r0 + r1 * tau */
typedef struct {
    int64_t r0;
    int64_t r1;
} koblitz_ztau_t;

/* Дескриптор доменних параметрів кривої Кобліца */
typedef struct {
    uint16_t m;                    /* Степінь розширення поля (163, 233, 283, 409, 571) */
    uint8_t a;                     /* Коефіцієнт кривої a in {0, 1} */
    int8_t mu;                     /* Параметр ендоморфізму mu = (-1)^{1-a} in {-1, +1} */
    uint8_t h;                     /* Кофактор кривої h in {2, 4} */
    size_t num_words;              /* Кількість 64-бітних слів для представлення поля */
    uint64_t top_word_mask;        /* Бітова маска для нормалізації старшого слова */
    koblitz_fe_t poly;             /* Незвідний многочлен поля f(x) */
    koblitz_fe_t r;                /* Порядок криптографічної підгрупи r */
    koblitz_affine_point_t G;      /* Базова точка генератора G */
} koblitz_params_t;

/* Таблиця попередньо обчислених кратних точок для w-TNAF (w=4) */
typedef struct {
    koblitz_affine_point_t points[8]; /* Точки [alpha_u]P для непарних u */
    size_t count;
} koblitz_precomp_table_t;
