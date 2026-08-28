/* third_party/legacy_codec/codec.c */
#include "codec.h"
#include <stdio.h>
#include <string.h>

int legacy_encode(const char *input, size_t input_len, char *output, size_t max_out) {
    if (!input || !output || max_out < input_len + 1) {
        return -1;
    }
#ifdef CODEC_VERBOSE
    fprintf(stderr, "[codec] Encoding %zu bytes of stream\n", input_len);
#endif
    for (size_t i = 0; i < input_len; ++i) {
        output[i] = (char)(input[i] ^ 0x5A);
    }
    output[input_len] = '\0';
    return (int)input_len;
}
