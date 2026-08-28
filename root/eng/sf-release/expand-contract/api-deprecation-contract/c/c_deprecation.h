/* c_deprecation.h — Застарівання для C99/C11/C23 */
#ifndef C_DEPRECATION_H
#define C_DEPRECATION_H

#include <stddef.h>
#include <stdbool.h>

#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 202311L
#  define API_DEPRECATED(msg) [[deprecated(msg)]]
#elif defined(__GNUC__) || defined(__clang__)
#  define API_DEPRECATED(msg) __attribute__((deprecated(msg)))
#elif defined(_MSC_VER)
#  define API_DEPRECATED(msg) __declspec(deprecated(msg))
#else
#  define API_DEPRECATED(msg)
#endif

typedef struct {
    const char* user_id;
    const char* tenant_id;
    unsigned int flags;
} user_options_t;

/* Застаріла функція: компілятор видасть warning при її виклику */
API_DEPRECATED("legacy_get_user is deprecated. Migrate to user_store_find before v3.0 release.")
int legacy_get_user(const char* id, char* out_buf, size_t buf_len);

/* Новий розширений контракт */
int user_store_find(const user_options_t* opts, char* out_buf, size_t buf_len);

#endif /* C_DEPRECATION_H */
