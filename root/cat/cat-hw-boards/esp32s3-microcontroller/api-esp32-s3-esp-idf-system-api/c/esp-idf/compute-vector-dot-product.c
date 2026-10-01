#include "esp_nn.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "ESP_NN_VECTOR";

// Обчислення скалярного добутку двох векторів із залученням співпроцесора PIE
int32_t compute_vector_dot_product(const int8_t *vec_a, const int8_t *vec_b, size_t size) {
    // Векторні дані мають бути вирівняні по межі 16 байтів
    if (((uintptr_t)vec_a % 16 != 0) || ((uintptr_t)vec_b % 16 != 0)) {
        ESP_LOGW(TAG, "Увага: Векторні масиви не вирівняні по межі 16 байтів!");
    }
    
    int32_t result = 0;
    // Виклик оптимізованої функції з бібліотеки ESP-NN
    esp_nn_dot_product_s8(vec_a, vec_b, size, &result);
    
    return result;
}

void demo_vector_calculation(void) {
    const size_t vector_size = 64; // Розмір має бути кратним розміру вектора PIE
    
    // Виділення 16-байтово вирівняної пам'яті у внутрішній SRAM
    int8_t *array1 = (int8_t *)heap_caps_aligned_alloc(16, vector_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    int8_t *array2 = (int8_t *)heap_caps_aligned_alloc(16, vector_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    
    if (array1 && array2) {
        for (size_t i = 0; i < vector_size; i++) {
            array1[i] = (int8_t)(i % 10);
            array2[i] = (int8_t)(2);
        }
        
        int32_t dot_prod = compute_vector_dot_product(array1, array2, vector_size);
        ESP_LOGI(TAG, "Результат векторного скалярного добутку: %" PRIi32, dot_prod);
        
        heap_caps_free(array1);
        heap_caps_free(array2);
    }
}
