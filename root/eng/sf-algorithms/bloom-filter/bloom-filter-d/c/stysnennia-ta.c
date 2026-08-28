#include <stdint.h>
#include <size_t.h>

/* Просте RLE-стиснення послідовностей нульових байтів у C */
size_t bloom_compress_rle(const uint8_t *in, size_t in_bytes, uint8_t *out) {
    size_t out_idx = 0;
    for (size_t i = 0; i < in_bytes; ) {
        if (in[i] == 0x00) {
            size_t zeros = 0;
            while (i < in_bytes && in[i] == 0x00 && zeros < 255) { zeros++; i++; }
            out[out_idx++] = 0x00;
            out[out_idx++] = (uint8_t)zeros;
        } else {
            out[out_idx++] = in[i++];
        }
    }
    return out_idx;
}
