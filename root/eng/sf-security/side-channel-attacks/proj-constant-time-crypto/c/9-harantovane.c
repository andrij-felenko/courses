#include <stdint.h>
#include <stddef.h>

/* Гарантоване занулення пам'яті, яке ніколи не видаляється компілятором */
void ct_secure_zero(void *ptr, size_t len) {
    #if defined(__STDC_LIB_EXT1__)
    memset_s(ptr, len, 0, len);
    #elif defined(_MSC_VER)
    SecureZeroMemory(ptr, len);
    #elif defined(__GLIBC__) || defined(__FreeBSD__) || defined(__OpenBSD__)
    explicit_bzero(ptr, len);
    #else
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0;
    }
    __asm__ volatile ("" : : "r" (ptr) : "memory");
    #endif
}
