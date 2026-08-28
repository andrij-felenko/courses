#include <stdint.h>
#include <stddef.h>
#include <x86intrin.h>

/* Безгалузеве маскування індексу (Branchless Sanitization) */
static inline size_t sanitize_speculative_index(size_t index, size_t limit) {
    /* Якщо index < limit, старший біт різниці дорівнює 0, маска = 0xFFFFFFFFFFFFFFFF;
       якщо index >= limit, маска стає 0x0000000000000000 */
    int64_t mask = ((int64_t)(index ^ limit) | (int64_t)(index - limit)) >> 63;
    return index & (size_t)(~mask);
}

/* Читання елемента з апаратним бар'єром LFENCE */
uint8_t secure_read_with_fence(const uint8_t *arr, size_t len, size_t idx) {
    if (idx < len) {
        _mm_lfence(); /* Повна зупинка спекулятивного конвеєра */
        return arr[idx];
    }
    return 0;
}
