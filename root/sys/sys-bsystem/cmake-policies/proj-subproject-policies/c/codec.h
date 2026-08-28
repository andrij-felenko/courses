/* third_party/legacy_codec/codec.h */
#ifndef CODEC_H
#define CODEC_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

int legacy_encode(const char *input, size_t input_len, char *output, size_t max_out);

#ifdef __cplusplus
}
#endif

#endif /* CODEC_H */
