#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Допоміжні бітові операції для підрахунку провідних і кінцевих нулів */
#if defined(__GNUC__) || defined(__clang__)
static inline int count_leading_zeros64(uint64_t x) {
    return x == 0 ? 64 : __builtin_clzll(x);
}
static inline int count_trailing_zeros64(uint64_t x) {
    return x == 0 ? 64 : __builtin_ctzll(x);
}
#else
static inline int count_leading_zeros64(uint64_t x) {
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
static inline int count_trailing_zeros64(uint64_t x) {
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
    uint8_t *buffer;
    size_t capacity;
    size_t byte_pos;
    uint8_t bit_pos; /* 0..7: кількість вільних бітів у поточному байті */
} BitWriter;

static void bit_writer_init(BitWriter *bw, uint8_t *buf, size_t cap) {
    bw->buffer = buf;
    bw->capacity = cap;
    bw->byte_pos = 0;
    bw->bit_pos = 8;
    if (cap > 0) bw->buffer[0] = 0;
}

static void bit_writer_write_bits(BitWriter *bw, uint64_t value, int num_bits) {
    for (int i = num_bits - 1; i >= 0; --i) {
        if (bw->byte_pos >= bw->capacity) return;
        uint8_t bit = (uint8_t)((value >> i) & 1ULL);
        bw->bit_pos--;
        bw->buffer[bw->byte_pos] |= (uint8_t)(bit << bw->bit_pos);
        if (bw->bit_pos == 0) {
            bw->bit_pos = 8;
            bw->byte_pos++;
            if (bw->byte_pos < bw->capacity) {
                bw->buffer[bw->byte_pos] = 0;
            }
        }
    }
}

static size_t bit_writer_flush(BitWriter *bw) {
    if (bw->bit_pos < 8) {
        return bw->byte_pos + 1;
    }
    return bw->byte_pos;
}

typedef struct {
    BitWriter bw;
    uint64_t prev_time;
    uint64_t prev_delta;
    uint64_t prev_val_bits;
    int prev_leading;
    int prev_trailing;
    size_t count;
} GorillaEncoder;

void gorilla_encoder_init(GorillaEncoder *enc, uint8_t *buf, size_t cap) {
    bit_writer_init(&enc->bw, buf, cap);
    enc->prev_time = 0;
    enc->prev_delta = 0;
    enc->prev_val_bits = 0;
    enc->prev_leading = 64;
    enc->prev_trailing = 64;
    enc->count = 0;
}

static void encode_timestamp(GorillaEncoder *enc, uint64_t t) {
    if (enc->count == 0) {
        bit_writer_write_bits(&enc->bw, t, 64);
        enc->prev_time = t;
        return;
    }
    if (enc->count == 1) {
        uint64_t delta = t - enc->prev_time;
        bit_writer_write_bits(&enc->bw, delta, 14);
        enc->prev_delta = delta;
        enc->prev_time = t;
        return;
    }

    uint64_t delta = t - enc->prev_time;
    int64_t dod = (int64_t)delta - (int64_t)enc->prev_delta;

    if (dod == 0) {
        bit_writer_write_bits(&enc->bw, 0, 1);
    } else if (dod >= -63 && dod <= 64) {
        bit_writer_write_bits(&enc->bw, 2, 2); /* Префікс '10' */
        bit_writer_write_bits(&enc->bw, (uint64_t)(dod & 0x7F), 7);
    } else if (dod >= -255 && dod <= 256) {
        bit_writer_write_bits(&enc->bw, 6, 3); /* Префікс '110' */
        bit_writer_write_bits(&enc->bw, (uint64_t)(dod & 0x1FF), 9);
    } else if (dod >= -2047 && dod <= 2048) {
        bit_writer_write_bits(&enc->bw, 14, 4); /* Префікс '1110' */
        bit_writer_write_bits(&enc->bw, (uint64_t)(dod & 0xFFF), 12);
    } else {
        bit_writer_write_bits(&enc->bw, 15, 4); /* Префікс '1111' */
        bit_writer_write_bits(&enc->bw, (uint32_t)dod, 32);
    }

    enc->prev_delta = delta;
    enc->prev_time = t;
}

static void encode_value(GorillaEncoder *enc, double val) {
    uint64_t val_bits;
    memcpy(&val_bits, &val, sizeof(double));

    if (enc->count == 0) {
        bit_writer_write_bits(&enc->bw, val_bits, 64);
        enc->prev_val_bits = val_bits;
        return;
    }

    uint64_t xor_val = val_bits ^ enc->prev_val_bits;
    if (xor_val == 0) {
        bit_writer_write_bits(&enc->bw, 0, 1);
    } else {
        bit_writer_write_bits(&enc->bw, 1, 1);

        int leading = count_leading_zeros64(xor_val);
        int trailing = count_trailing_zeros64(xor_val);
        if (leading >= 32) leading = 31;

        if (enc->prev_leading != 64 &&
            leading >= enc->prev_leading &&
            trailing >= enc->prev_trailing) {
            bit_writer_write_bits(&enc->bw, 0, 1);
            int meaningful_len = 64 - enc->prev_leading - enc->prev_trailing;
            uint64_t meaningful_bits = (xor_val >> enc->prev_trailing);
            bit_writer_write_bits(&enc->bw, meaningful_bits, meaningful_len);
        } else {
            bit_writer_write_bits(&enc->bw, 1, 1);
            bit_writer_write_bits(&enc->bw, (uint64_t)leading, 5);
            int meaningful_len = 64 - leading - trailing;
            bit_writer_write_bits(&enc->bw, (uint64_t)meaningful_len, 6);
            uint64_t meaningful_bits = (xor_val >> trailing);
            bit_writer_write_bits(&enc->bw, meaningful_bits, meaningful_len);

            enc->prev_leading = leading;
            enc->prev_trailing = trailing;
        }
    }

    enc->prev_val_bits = val_bits;
}

void gorilla_encoder_add(GorillaEncoder *enc, uint64_t timestamp, double value) {
    encode_timestamp(enc, timestamp);
    encode_value(enc, value);
    enc->count++;
}

size_t gorilla_encoder_finish(GorillaEncoder *enc) {
    return bit_writer_flush(&enc->bw);
}
