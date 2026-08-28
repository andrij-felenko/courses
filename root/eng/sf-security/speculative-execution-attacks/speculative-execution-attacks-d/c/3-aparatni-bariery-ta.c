#include <stdint.h>
#include <stddef.h>
#include <x86intrin.h>

uint8_t secure_array_access(const uint8_t *arr, size_t len, size_t index) {
    if (index < len) {
        /* lfence блокує виконання наступних команд до розв'язання гілки */
        _mm_lfence();
        return arr[index];
    }
    return 0;
}
