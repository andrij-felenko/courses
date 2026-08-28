#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define VECTOR_LEN 1024

/* Векторизована фільтрація стовпця цілих чисел:
   Формує вектор вибірки (selection vector) без розгалужень у тілі циклу */
size_t filter_vector_i32(const int32_t* restrict column, 
                         size_t count, 
                         int32_t threshold, 
                         uint16_t* restrict sel_vector) {
    size_t matches = 0;
    
    /* Компілятор розгортає цей цикл за допомогою SIMD векторів (AVX2/AVX-512) */
    for (size_t i = 0; i < count; ++i) {
        bool pass = (column[i] > threshold);
        sel_vector[matches] = (uint16_t)i;
        matches += pass ? 1 : 0;
    }
    
    return matches;
}
