#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#if defined(__GNUC__) || defined(__clang__)
#define clz64(x) ((x) == 0 ? 64 : __builtin_clzll(x))
#define ctz64(x) ((x) == 0 ? 64 : __builtin_ctzll(x))
#else
static inline int clz64(uint64_t x) {
    if (x == 0) return 64;
    int n = 0;
    if ((x & 0xFFFFFFFF00000000ULL) == 0) { n += 32; x <<= 32; }
    if ((x & 0xFFFF000000000000ULL) == 0) { n += 16; x <<= 16; }
    if ((x & 0xFF00000000000000ULL) == 0) { n += 8;  x <<= 8;  }
    if ((x & 0xF000000000000000ULL) == 0) { n += 4;  x <<= 4;  }
    if ((x & 0xC000000000000000ULL) == 0) { n += 2;  x <<= 2;  }
    if ((x & 0x8000000000000000ULL) == 0) { n += 1; }
    return n;
}
static inline int ctz64(uint64_t x) {
    if (x == 0) return 64;
    int n = 0;
    if ((x & 0x00000000FFFFFFFFULL) == 0) { n += 32; x >>= 32; }
    if ((x & 0x000000000000FFFFULL) == 0) { n += 16; x >>= 16; }
    if ((x & 0x00000000000000FFULL) == 0) { n += 8;  x >>= 8;  }
    if ((x & 0x000000000000000FULL) == 0) { n += 4;  x >>= 4;  }
    if ((x & 0x0000000000000003ULL) == 0) { n += 2;  x >>= 2;  }
    if ((x & 0x0000000000000001ULL) == 0) { n += 1; }
    return n;
}
#endif

typedef struct {
    uint64_t prev_val_bits;
    int prev_leading;
    int prev_trailing;
    bool is_first;
} FloatXorEncoder;

void float_xor_init(FloatXorEncoder *enc) {
    enc->prev_val_bits = 0;
    enc->prev_leading = 64;
    enc->prev_trailing = 64;
    enc->is_first = true;
}

/* Кодування одного значення float64 через XOR */
void encode_float_step(FloatXorEncoder *enc, double val, 
                       uint64_t *out_payload, int *out_len) {
    uint64_t bits;
    memcpy(&bits, &val, sizeof(double));

    if (enc->is_first) {
        *out_payload = bits;
        *out_len = 64;
        enc->prev_val_bits = bits;
        enc->is_first = false;
        return;
    }

    uint64_t xor_val = bits ^ enc->prev_val_bits;
    enc->prev_val_bits = bits;

    if (xor_val == 0) {
        *out_payload = 0; /* Біт '0' */
        *out_len = 1;
        return;
    }

    int leading = clz64(xor_val);
    int trailing = ctz64(xor_val);
    if (leading >= 32) leading = 31;

    if (enc->prev_leading != 64 && 
        leading >= enc->prev_leading && 
        trailing >= enc->prev_trailing) {
        /* Межі вписуються у попереднє вікно */
        int meaningful_len = 64 - enc->prev_leading - enc->prev_trailing;
        uint64_t meaningful_bits = xor_val >> enc->prev_trailing;
        /* Формуємо біти: префікс '10' (2 біти) + значущі біти */
        *out_payload = (2ULL << meaningful_len) | (meaningful_bits & ((1ULL << meaningful_len) - 1));
        *out_len = 2 + meaningful_len;
    } else {
        /* Нове вікно */
        int meaningful_len = 64 - leading - trailing;
        uint64_t meaningful_bits = xor_val >> trailing;
        enc->prev_leading = leading;
        enc->prev_trailing = trailing;
        
        /* Запис вимагає кількох полів (префікс '11' + 5 біт leading + 6 біт len + payload) */
        *out_payload = meaningful_bits;
        *out_len = 2 + 5 + 6 + meaningful_len;
    }
}
