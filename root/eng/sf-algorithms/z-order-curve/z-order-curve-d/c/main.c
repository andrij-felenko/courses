#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#if defined(__x86_64__) || defined(_M_X64)
#include <immintrin.h>
#define HAS_BMI2 1
#endif

// Розсунення бітів 32-бітного числа на парні позиції (SWAR)
static uint64_t spread_bits32(uint32_t v) {
    uint64_t x = v & 0xFFFFFFFFULL;
    x = (x | (x << 16)) & 0x0000FFFF0000FFFFULL;
    x = (x | (x <<  8)) & 0x00FF00FF00FF00FFULL;
    x = (x | (x <<  4)) & 0x0F0F0F0F0F0F0F0FULL;
    x = (x | (x <<  2)) & 0x3333333333333333ULL;
    x = (x | (x <<  1)) & 0x5555555555555555ULL;
    return x;
}

// 2D кодування Morton (з підтримкою апаратного прискорення BMI2 PDEP)
uint64_t morton_encode2d(uint32_t x, uint32_t y) {
#if defined(HAS_BMI2)
    return _pdep_u64((uint64_t)x, 0x5555555555555555ULL) |
           _pdep_u64((uint64_t)y, 0xAAAAAAAAAAAAAAAAULL);
#else
    return spread_bits32(x) | (spread_bits32(y) << 1);
#endif
}

typedef struct {
    uint32_t x, y;
    uint64_t morton_key;
} Point2D;

typedef struct {
    uint32_t min_x, max_x;
    uint32_t min_y, max_y;
} BoundingBox2D;

// Перевірка точки у прямокутнику
static inline bool point_in_box(const Point2D *pt, const BoundingBox2D *box) {
    return (pt->x >= box->min_x && pt->x <= box->max_x &&
            pt->y >= box->min_y && pt->y <= box->max_y);
}

// Простірний віконний запит над впорядкованим масивом Z-точок
size_t morton_range_query(const Point2D *points, size_t count,
                          const BoundingBox2D *box,
                          Point2D *out_results, size_t max_results) {
    if (count == 0 || max_results == 0) return 0;

    uint64_t min_key = morton_encode2d(box->min_x, box->min_y);
    uint64_t max_key = morton_encode2d(box->max_x, box->max_y);

    size_t found = 0;
    for (size_t i = 0; i < count; ++i) {
        uint64_t k = points[i].morton_key;
        if (k < min_key) continue;
        if (k > max_key) break; // Ранній вихід за межу Z-коду

        if (point_in_box(&points[i], box)) {
            out_results[found++] = points[i];
            if (found >= max_results) break;
        }
    }
    return found;
}
