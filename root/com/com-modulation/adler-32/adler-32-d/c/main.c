#include <stdint.h>
#include <stddef.h>

#define MOD 65521

uint32_t adler32(const uint8_t *data, size_t len) {
    uint32_t a = 1, b = 0;
    for (size_t i = 0; i < len; i++) {
        a = (a + data[i]) % MOD;   // сума байтів
        b = (b + a)       % MOD;   // сума значень A — зважує байт позицією
    }
    return (b << 16) | a;          // B у старші 16 біт, A — у молодші
}
