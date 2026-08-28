#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/* НЕБЕЗПЕЧНО: Ранній вихід дозволяє побайтовий підбір тегу */
bool vulnerable_verify_mac(const uint8_t *expected, const uint8_t *received, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        if (expected[i] != received[i]) {
            return false; /* Час відповіді залежить від позиції першої помилки */
        }
    }
    return true;
}
