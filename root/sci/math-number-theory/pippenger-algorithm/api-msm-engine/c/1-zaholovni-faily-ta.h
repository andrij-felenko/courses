#ifndef MSM_ENGINE_H
#define MSM_ENGINE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок виконання операцій MSM */
typedef enum {
    MSM_SUCCESS             =  0,  /* Успішне завершення обчислення */
    MSM_ERR_NULL_PTR        = -1,  /* Передано нульовий вказівник */
    MSM_ERR_INVALID_SIZE    = -2,  /* Некоректний розмір масиву (n == 0 або невідповідність довжин) */
    MSM_ERR_OUT_OF_MEMORY   = -3,  /* Недостатньо оперативної пам'яті для розміщення кошиків */
    MSM_ERR_INVALID_CURVE   = -4,  /* Непідтримуваний ідентифікатор еліптичної кривої */
    MSM_ERR_POINT_NOT_ON_EC = -5,  /* Вхідна точка не задовольняє рівняння кривої */
    MSM_ERR_BACKEND_FAILED  = -6,  /* Збій апаратного прискорювача (CUDA error / OpenCL error) */
    MSM_ERR_INVALID_CONFIG  = -7   /* Некоректні параметри конфігурації (неприпустима ширина вікна) */
} msm_status_t;

/* Ідентифікатор підтримуваних еліптичних кривих */
typedef enum {
    MSM_CURVE_BN254     = 1,   /* Крива BN254 (alt_bn128, Ethereum) */
    MSM_CURVE_BLS12_381 = 2,   /* Крива BLS12-381 (Zcash, Filecoin, Ethereum 2.0) */
    MSM_CURVE_SECP256K1 = 3    /* Крива secp256k1 (Bitcoin, EVM precompiles) */
} msm_curve_id_t;

/* Тип обчислювального бекенду */
typedef enum {
    MSM_BACKEND_CPU_SCALAR  = 0,  /* Базовий скалярний CPU-рушій (сумісний з будь-якою архітектурою) */
    MSM_BACKEND_CPU_AVX512  = 1,  /* Векторизований CPU-рушій AVX-512 IFMA (52-бітне множення) */
    MSM_BACKEND_GPU_CUDA    = 2   /* Графічний прискорювач NVIDIA CUDA */
} msm_backend_t;

/* 256-бітний елемент поля у формі Монтгомері (4 слова по 64 біти) */
typedef struct {
    uint64_t limbs[4];
} msm_fe256_t;

/* Точка еліптичної кривої в афінних координатах (x, y) */
typedef struct {
    msm_fe256_t x;
    msm_fe256_t y;
    bool is_infinity;
} msm_point_affine_t;

/* Проективна точка в координатах Якобі (X, Y, Z), де x = X/Z^2, y = Y/Z^3 */
typedef struct {
    msm_fe256_t X;
    msm_fe256_t Y;
    msm_fe256_t Z;
} msm_point_jacobian_t;

/* Конфігурація параметрів виконання MSM */
typedef struct {
    msm_curve_id_t curve;      /* Використовувана еліптична крива */
    msm_backend_t backend;     /* Обраний обчислювальний бекенд */
    uint32_t window_size;      /* Ширина вікна c (0 = автоматичний вибір за розміром n) */
    uint32_t num_threads;      /* Кількість паралельних потоків (0 = auto / CPU cores) */
    bool use_signed_digits;    /* Використовувати знакове wNAF-розбиття (зменшує кошики удвічі) */
    bool enable_radix_sort;    /* Увімкнути порозрядне групування точок для оптимізації кешу */
    void *custom_arena_buffer; /* Попередньо виділена пам'ять для кошиків (опціонально) */
    size_t custom_arena_size;  /* Розмір буфера арени у байтах */
} msm_config_t;

#ifdef __cplusplus
}
#endif

#endif /* MSM_ENGINE_H */
