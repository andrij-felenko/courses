#include <stdio.h>
#include "esp_attr.h"
#include "esp_dsp.h"

// Приклад векторного множення масивів 16-бітних чисел за допомогою інтринсиків PIE
void IRAM_ATTR vector_dot_product_s16(const int16_t *src_a, const int16_t *src_b, int32_t *result, size_t count) {
    // Операція обробляє по 8 елементів (128 біт) за одну ітерацію циклу
    size_t vector_iters = count / 8;
    int32_t accum = 0;

    for (size_t i = 0; i < vector_iters; i++) {
        // Завантаження 128-бітних векторних операндів у регістри PIE
        ae_valign align_a = AE_LA64_PP(src_a + i * 8);
        ae_valign align_b = AE_LA64_PP(src_b + i * 8);
        
        // Виконання паралельного множення з накопиченням
        // Інструкція обробляє вісім 16-бітних пар одночасно
        accum += dsps_dotprod_s16_ansi(src_a + i * 8, src_b + i * 8, 8, 0);
    }
    *result = accum;
}
