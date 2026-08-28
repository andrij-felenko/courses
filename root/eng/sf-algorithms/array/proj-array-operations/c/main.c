#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

// 64 байти — розмір стандартної кеш-лінії x86/ARM для оптимізації SIMD
#define CACHE_LINE_ALIGN 64
#define INITIAL_CAPACITY 4
#define GROWTH_FACTOR 2

typedef struct {
    int *data;
    size_t size;
    size_t capacity;
} VectorC;

// Ініціалізація вектора з апаратним вирівнюванням пам'яті
bool vector_init(VectorC *vec, size_t initial_cap) {
    if (!vec) return false;
    
    vec->size = 0;
    vec->capacity = (initial_cap > 0) ? initial_cap : INITIAL_CAPACITY;
    
    // Виділення пам'яті, кратної CACHE_LINE_ALIGN
    size_t bytes = vec->capacity * sizeof(int);
    // Вирівнюємо загальний розмір виділення до кратного alignment
    size_t aligned_bytes = (bytes + CACHE_LINE_ALIGN - 1) & ~(CACHE_LINE_ALIGN - 1);
    
    #if defined(_MSC_VER)
    vec->data = (int *)_aligned_malloc(aligned_bytes, CACHE_LINE_ALIGN);
    #else
    vec->data = (int *)aligned_alloc(CACHE_LINE_ALIGN, aligned_bytes);
    #endif

    if (!vec->data) {
        vec->capacity = 0;
        return false;
    }
    return true;
}

// Звільнення пам'яті
void vector_free(VectorC *vec) {
    if (vec && vec->data) {
        #if defined(_MSC_VER)
        _aligned_free(vec->data);
        #else
        free(vec->data);
        #endif
        vec->data = NULL;
        vec->size = 0;
        vec->capacity = 0;
    }
}

// Зміна місткості при досягненні ліміту
static bool vector_reserve(VectorC *vec, size_t new_cap) {
    if (new_cap <= vec->capacity) return true;
    
    size_t bytes = new_cap * sizeof(int);
    size_t aligned_bytes = (bytes + CACHE_LINE_ALIGN - 1) & ~(CACHE_LINE_ALIGN - 1);
    
    int *new_data = NULL;
    #if defined(_MSC_VER)
    new_data = (int *)_aligned_realloc(vec->data, aligned_bytes, CACHE_LINE_ALIGN);
    #else
    new_data = (int *)aligned_alloc(CACHE_LINE_ALIGN, aligned_bytes);
    if (new_data && vec->data) {
        memcpy(new_data, vec->data, vec->size * sizeof(int));
        free(vec->data);
    }
    #endif

    if (!new_data) return false;
    
    vec->data = new_data;
    vec->capacity = new_cap;
    return true;
}

// Вставка елемента в кінець: амортизовано O(1)
bool vector_push_back(VectorC *vec, int value) {
    if (vec->size >= vec->capacity) {
        size_t new_cap = vec->capacity * GROWTH_FACTOR;
        if (!vector_reserve(vec, new_cap)) return false;
    }
    vec->data[vec->size++] = value;
    return true;
}

// Безпечне отримання елемента за індексом
bool vector_get(const VectorC *vec, size_t index, int *out_val) {
    if (!vec || index >= vec->size || !out_val) return false;
    *out_val = vec->data[index];
    return true;
}

int main(void) {
    VectorC vec;
    if (!vector_init(&vec, 4)) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    for (int i = 0; i < 10; ++i) {
        vector_push_back(&vec, i * 10);
    }

    printf("Розмір C-вектора: %zu, Місткість: %zu\n", vec.size, vec.capacity);
    for (size_t i = 0; i < vec.size; ++i) {
        int val;
        vector_get(&vec, i, &val);
        printf("[%zu] = %d\n", i, val);
    }

    vector_free(&vec);
    return 0;
}
