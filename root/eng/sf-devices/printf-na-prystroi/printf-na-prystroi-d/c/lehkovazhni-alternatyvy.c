#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>

/* Швидке перетворення беззнакового цілого в рядок без виклику libc */
static size_t fast_utoa(uint32_t val, char *buf) {
    char temp[11];
    size_t i = 0;
    
    if (val == 0) {
        buf[0] = '0';
        return 1;
    }
    
    while (val > 0) {
        temp[i++] = (char)('0' + (val % 10U));
        val /= 10U;
    }
    
    /* Розвертаємо символи у вихідний буфер */
    for (size_t j = 0; j < i; ++j) {
        buf[j] = temp[i - 1U - j];
    }
    return i;
}

/* Приклад легковажного форматування без залежностей від malloc та float */
int mini_snprintf(char *out, size_t max_len, const char *fmt, ...) {
    if (max_len == 0 || out == NULL || fmt == NULL) {
        return 0;
    }
    
    va_list args;
    va_start(args, fmt);
    
    size_t written = 0;
    while (*fmt != '\0' && written + 1 < max_len) {
        if (*fmt == '%' && *(fmt + 1) != '\0') {
            fmt++;
            if (*fmt == 'u') {
                uint32_t u = va_arg(args, uint32_t);
                char num_buf[11];
                size_t num_len = fast_utoa(u, num_buf);
                for (size_t k = 0; k < num_len && (written + 1 < max_len); ++k) {
                    out[written++] = num_buf[k];
                }
            } else if (*fmt == 's') {
                const char *s = va_arg(args, const char*);
                if (s == NULL) s = "(null)";
                while (*s != '\0' && written + 1 < max_len) {
                    out[written++] = *s++;
                }
            } else if (*fmt == '%') {
                out[written++] = '%';
            }
        } else {
            out[written++] = *fmt;
        }
        fmt++;
    }
    
    out[written] = '\0';
    va_end(args);
    return (int)written;
}
