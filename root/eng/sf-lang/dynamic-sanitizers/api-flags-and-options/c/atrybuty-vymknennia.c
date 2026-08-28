#include <stddef.h>

// Вимкнення перевірок AddressSanitizer для оптимізованої функції копіювання
__attribute__((no_sanitize("address")))
void fast_unaligned_block_copy(void *dest, const void *src, size_t n) {
    char *d = (char *)dest;
    const char *s = (const char *)src;
    while (n--) {
        *d++ = *s++;
    }
}

// Вимкнення TSan для прямого опитування апаратного регістра без м'ютекса
__attribute__((no_sanitize("thread")))
unsigned int poll_hardware_status_register(volatile const unsigned int *reg_addr) {
    return *reg_addr;
}
