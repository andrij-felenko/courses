#include <stdint.h>
#include <stddef.h>

// Обчислення коректного циклічного індексу у буфері розміру N
size_t ring_buffer_wrap_index(int32_t index, size_t buffer_size) {
    if (buffer_size == 0) return 0;
    
    int32_t n = (int32_t)buffer_size;
    int32_t rem = index % n;
    
    // Коригуємо від'ємну остачу C99 у додатній діапазон [0, N-1]
    if (rem < 0) {
        rem += n;
    }
    return (size_t)rem;
}
