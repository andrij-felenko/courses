#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FIELD_WORDS 4

/* 256-бітне велике число у формі 4 слів по 64 біти */
typedef struct {
    uint64_t d[FIELD_WORDS];
} fe256_t;

/* Точка еліптичної кривої в афінних координатах (x, y) */
typedef struct {
    fe256_t x;
    fe256_t y;
    bool is_infinity;
} point_affine_t;

/* Точка еліптичної кривої в координатах Якобі (X, Y, Z) */
typedef struct {
    fe256_t X;
    fe256_t Y;
    fe256_t Z;
} point_jacobian_t;
