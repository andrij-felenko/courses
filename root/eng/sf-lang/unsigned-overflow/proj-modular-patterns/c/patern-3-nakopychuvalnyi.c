#include <stdint.h>
#include <stddef.h>

#define FNV_OFFSET_32  2166136261u    // 0x811C9DC5
#define FNV_PRIME_32   16777619u      // 0x01000193

uint32_t fnv1a_32(const uint8_t *data, size_t len) {
    uint32_t hash = FNV_OFFSET_32;
    for (size_t i = 0; i < len; i++) {
        hash ^= data[i];              // XOR молодшого байта
        hash *= FNV_PRIME_32;         // множення з wrap за модулем 2³² — НАВМИСНЕ
    }
    return hash;
}
