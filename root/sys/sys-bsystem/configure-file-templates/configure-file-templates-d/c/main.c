/* C-код із директивою #if */
#include "app/config.h"

int compress_payload(const uint8_t* src, size_t len, uint8_t* dst) {
#if HAVE_ZSTD
    return zstd_compress(src, len, dst);
#else
    return raw_copy(src, len, dst);
#endif
}
