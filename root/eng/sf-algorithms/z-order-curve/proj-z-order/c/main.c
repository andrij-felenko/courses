#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#if defined(__x86_64__) || defined(_M_X64)
#include <immintrin.h>
#define HAS_BMI2 1
#endif

// -----------------------------------------------------------------------------
// 1. Розсування бітів 32-бітного числа (SWAR magic masks)
// Біти 0..31 переміщуються на парні позиції 0, 2, 4, ..., 62
// -----------------------------------------------------------------------------
static uint64_t spread_bits32(uint32_t v) {
    uint64_t x = v & 0xFFFFFFFFULL;
    x = (x | (x << 16)) & 0x0000FFFF0000FFFFULL;
    x = (x | (x <<  8)) & 0x00FF00FF00FF00FFULL;
    x = (x | (x <<  4)) & 0x0F0F0F0F0F0F0F0FULL;
    x = (x | (x <<  2)) & 0x3333333333333333ULL;
    x = (x | (x <<  1)) & 0x5555555555555555ULL;
    return x;
}

// Стискання парних бітів назад у 32-бітне число
static uint32_t compact_bits64(uint64_t v) {
    uint64_t x = v & 0x5555555555555555ULL;
    x = (x | (x >>  1)) & 0x3333333333333333ULL;
    x = (x | (x >>  2)) & 0x0F0F0F0F0F0F0F0FULL;
    x = (x | (x >>  4)) & 0x00FF00FF00FF00FFULL;
    x = (x | (x >>  8)) & 0x0000FFFF0000FFFFULL;
    x = (x | (x >> 16)) & 0xFFFFFFFFULL;
    return (uint32_t)x;
}

// -----------------------------------------------------------------------------
// 2. Кодування та декодування Morton 2D
// -----------------------------------------------------------------------------
uint64_t morton_encode2d(uint32_t x, uint32_t y) {
#if defined(HAS_BMI2)
    // Маска для парних бітів 0x5555... і непарних 0xAAAA...
    return _pdep_u64((uint64_t)x, 0x5555555555555555ULL) |
           _pdep_u64((uint64_t)y, 0xAAAAAAAAAAAAAAAAULL);
#else
    return spread_bits32(x) | (spread_bits32(y) << 1);
#endif
}

void morton_decode2d(uint64_t z, uint32_t *x, uint32_t *y) {
#if defined(HAS_BMI2)
    *x = (uint32_t)_pext_u64(z, 0x5555555555555555ULL);
    *y = (uint32_t)_pext_u64(z, 0xAAAAAAAAAAAAAAAAULL);
#else
    *x = compact_bits64(z);
    *y = compact_bits64(z >> 1);
#endif
}

// -----------------------------------------------------------------------------
// 3. Структури просторових точок і прямокутного вікна
// -----------------------------------------------------------------------------
typedef struct {
    uint32_t x;
    uint32_t y;
    uint64_t morton_key;
} Point2D;

typedef struct {
    uint32_t min_x;
    uint32_t max_x;
    uint32_t min_y;
    uint32_t max_y;
} BoundingBox2D;

static bool point_in_box(uint32_t x, uint32_t y, const BoundingBox2D *box) {
    return (x >= box->min_x && x <= box->max_x &&
            y >= box->min_y && y <= box->max_y);
}

// -----------------------------------------------------------------------------
// 4. Пошук у відсортованому масиві Morton-точок
// -----------------------------------------------------------------------------
size_t morton_range_query(const Point2D *points, size_t count,
                          const BoundingBox2D *box,
                          Point2D *out_results, size_t max_results) {
    if (count == 0 || max_results == 0) return 0;

    uint64_t min_key = morton_encode2d(box->min_x, box->min_y);
    uint64_t max_key = morton_encode2d(box->max_x, box->max_y);

    size_t result_count = 0;

    for (size_t i = 0; i < count; ++i) {
        uint64_t k = points[i].morton_key;

        // Раннє відсікання поза основними межами Z-кодів
        if (k < min_key) continue;
        if (k > max_key) break;

        if (point_in_box(points[i].x, points[i].y, box)) {
            out_results[result_count++] = points[i];
            if (result_count >= max_results) break;
        }
    }

    return result_count;
}
