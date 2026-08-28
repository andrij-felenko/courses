#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Статуси повернення рішень API
typedef enum {
    BLS12_381_SUCCESS               = 0,
    BLS12_381_ERROR_INVALID_POINT   = 1,
    BLS12_381_ERROR_NOT_IN_GROUP    = 2,
    BLS12_381_ERROR_BUFFER_TOO_SMALL= 3,
    BLS12_381_ERROR_VERIFICATION_FAILED = 4,
    BLS12_381_ERROR_NULL_POINTER    = 5
} bls12_381_status_t;

// Елемент базового поля F_p (381 біт, 48 байт у формі Монтгомері)
typedef struct {
    uint64_t limbs[6]; // 6 * 64 = 384 біти
} bls12_381_fp_t;

// Елемент розширення F_{p^2} = F_p[u] / (u^2 + 1)
typedef struct {
    bls12_381_fp_t c0; // Реальність
    bls12_381_fp_t c1; // Уявність
} bls12_381_fp2_t;

// Елемент цільової групи Gt (поле F_{p^{12}}, 576 байт)
typedef struct {
    bls12_381_fp2_t c0[3]; // Нижня вежа F_{p^6}
    bls12_381_fp2_t c1[3]; // Верхня вежа F_{p^6}
} bls12_381_gt_t;

// Точка групи G1 у проєктивних координатах Якобі (X : Y : Z)
typedef struct {
    bls12_381_fp_t X;
    bls12_381_fp_t Y;
    bls12_381_fp_t Z;
} bls12_381_g1_projective_t;

// Точка групи G1 в афінних координатах (x, y)
typedef struct {
    bls12_381_fp_t x;
    bls12_381_fp_t y;
    bool infinity;
} bls12_381_g1_affine_t;

// Точка групи G2 у проєктивних координатах (X : Y : Z)
typedef struct {
    bls12_381_fp2_t X;
    bls12_381_fp2_t Y;
    bls12_381_fp2_t Z;
} bls12_381_g2_projective_t;

// Точка групи G2 в афінних координатах (x, y)
typedef struct {
    bls12_381_fp2_t x;
    bls12_381_fp2_t y;
    bool infinity;
} bls12_381_g2_affine_t;
