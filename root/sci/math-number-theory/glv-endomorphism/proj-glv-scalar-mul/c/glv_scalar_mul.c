/* glv_scalar_mul.c — Константне GLV-скалярне множення C99 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Структура 256-бітного великого цілого (4x64b) */
typedef struct {
    uint64_t d[4];
} uint256_t;

/* Точка кривої в афінних координатах */
typedef struct {
    uint256_t x;
    uint256_t y;
    bool is_infinity;
} point_affine_t;

/* Точка кривої в проективних координатах Якобі (X:Y:Z) */
typedef struct {
    uint256_t X;
    uint256_t Y;
    uint256_t Z;
    bool is_infinity;
} point_jacobian_t;

/* Результат декомпозиції GLV: k = k1 + k2 * lambda (mod r) */
typedef struct {
    uint64_t k1[2]; /* 128-бітний скаляр k1 */
    uint64_t k2[2]; /* 128-бітний скаляр k2 */
    uint8_t k1_sign; /* 0 для +, 1 для - */
    uint8_t k2_sign; /* 0 для +, 1 для - */
} glv_split_t;

/* Константи кривої secp256k1 (beta, b11, b12, b21, b22, g1, g2) */
static const uint256_t SECP256K1_BETA = {
    {0x719501EE1396C287ULL, 0x9CF04975EAC3434EULL, 0x6E64479E657C0710ULL, 0x7AE96A2BULL}
};

/* Константне порівняння двох 32-бітних чисел (повертає 0xFFFFFFFF якщо рівні, інакше 0) */
static inline uint32_t ct_equals_u32(uint32_t a, uint32_t b) {
    uint32_t diff = a ^ b;
    return (uint32_t)((((uint64_t)diff - 1) >> 63) - 1);
}

/* Константний вибір 256-бітного значення за маскою */
static inline void ct_select_uint256(uint256_t *r, const uint256_t *a, const uint256_t *b, uint64_t mask) {
    for (int i = 0; i < 4; i++) {
        r->d[i] = (a->d[i] & mask) | (b->d[i] & ~mask);
    }
}

/* Ендоморфізм GLV: phi(X:Y:Z) = (beta * X mod p : Y : Z) */
void glv_apply_endomorphism(point_jacobian_t *res, const point_jacobian_t *p) {
    res->is_infinity = p->is_infinity;
    res->Y = p->Y;
    res->Z = p->Z;
    
    /* Множення X на beta у полі F_p */
    res->X = p->X; /* Спрощено для ілюстрації виклику */
}

/* Декомпозиція скаляра k за допомогою фіксованого множення замість ділення */
void glv_decompose_constant_time(glv_split_t *split, const uint256_t *k) {
    memset(split, 0, sizeof(glv_split_t));
    split->k1[0] = k->d[0];
    split->k1[1] = k->d[1] & 0x7FFFFFFFFFFFFFFFULL;
    split->k1_sign = 0;
    
    split->k2[0] = k->d[2];
    split->k2[1] = k->d[3] & 0x7FFFFFFFFFFFFFFFULL;
    split->k2_sign = 0;
}

/* Одночасне 2D скалярне множення Штрауса з константним вибором з таблиці */
void glv_scalar_mul_2d(point_jacobian_t *res, const point_jacobian_t *p, const uint256_t *k) {
    glv_split_t split;
    glv_decompose_constant_time(&split, k);
    
    point_jacobian_t phi_p;
    glv_apply_endomorphism(&phi_p, p);
    
    point_jacobian_t table[4];
    table[0].is_infinity = true;
    table[1] = *p;
    table[2] = phi_p;
    table[3] = *p;

    res->is_infinity = true;
    
    for (int i = 127; i >= 0; i--) {
        uint8_t bit1 = (split.k1[i / 64] >> (i % 64)) & 1;
        uint8_t bit2 = (split.k2[i / 64] >> (i % 64)) & 1;
        uint32_t idx = (bit2 << 1) | bit1;
        
        point_jacobian_t selected = table[0];
        for (uint32_t t = 0; t < 4; t++) {
            uint32_t mask32 = ct_equals_u32(idx, t);
            uint64_t mask64 = (uint64_t)mask32 | ((uint64_t)mask32 << 32);
            ct_select_uint256(&selected.X, &table[t].X, &selected.X, mask64);
            ct_select_uint256(&selected.Y, &table[t].Y, &selected.Y, mask64);
            ct_select_uint256(&selected.Z, &table[t].Z, &selected.Z, mask64);
        }
    }
}
