#include <immintrin.h>
#include <stdint.h>

// Примусове скидання кеш-ліній буфера з усіх рівнів кешу
static void flush_buffer_from_cache(const void *addr, size_t bytes) {
    const char *ptr = (const char *)addr;
    for (size_t i = 0; i < bytes; i += 64) {
        _mm_clflushopt(ptr + i);
    }
    _mm_sfence(); // очікування завершення скидання
}
