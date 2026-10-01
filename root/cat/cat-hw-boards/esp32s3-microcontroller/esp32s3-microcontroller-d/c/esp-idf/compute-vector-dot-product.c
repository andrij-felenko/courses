#include <stdio.h>
#include <stdint.h>
#include "esp_nn.h"

// Оголошення векторних масивів із суворим 16-байтним вирівнюванням
static const int8_t vector_a[16] __attribute__((aligned(16))) = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
static const int8_t vector_b[16] __attribute__((aligned(16))) = {2, 2, 2, 2, 2, 2, 2, 2, 2,  2,  2,  2,  2,  2,  2,  2};

int32_t compute_vector_dot_product(const int8_t *src_a, const int8_t *src_b, size_t length) {
    int32_t result = 0;
    // Використання оптимізованого векторного ядра ESP-NN для розрахунку добутку int8
    esp_nn_dot_product_s8(src_a, src_b, length, &result);
    return result;
}

void app_main(void) {
    int32_t dot_product = compute_vector_dot_product(vector_a, vector_b, 16);
    printf("Векторний точковий добуток: %ld\n", (long)dot_product);
}
