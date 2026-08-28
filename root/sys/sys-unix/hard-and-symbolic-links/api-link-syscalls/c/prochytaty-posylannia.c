#include <stdlib.h>
#include <unistd.h>

/* Повертає шлях, завершений нулем; звільняє викликач. NULL — помилка. */
char *read_link(const char *path)
{
    size_t size = 256;
    for (;;) {
        char *buf = malloc(size);
        if (!buf)
            return NULL;
        ssize_t n = readlink(path, buf, size);
        if (n < 0) {            /* errno вже виставлено */
            free(buf);
            return NULL;
        }
        if ((size_t)n < size) { /* влізло з запасом — зрізати не могло */
            buf[n] = '\0';
            return buf;
        }
        free(buf);              /* n == size: могло зрізати, беремо більший */
        size *= 2;
    }
}
