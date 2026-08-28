#include <stddef.h>

/**
 * Обчислення максимального розміру буфера передавача (включно з кінцевим 0x00).
 */
#define COBS_ENCODED_MAX_SIZE(payload_size) \
    ((payload_size) + ((payload_size) / 254) + 1 + 1)

/**
 * Обчислення максимального розміру буфера корисного навантаження після розпакування.
 */
#define COBS_DECODED_MAX_SIZE(encoded_size) \
    ((encoded_size) > 1 ? ((encoded_size) - 1) : 0)
