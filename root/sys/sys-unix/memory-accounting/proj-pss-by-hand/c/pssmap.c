/* pssmap.c — зведення пам'яті процесу з /proc/<pid>/smaps.
 *   cc -O2 -Wall -o pssmap pssmap.c
 *   ./pssmap <pid> [рядків]   таблиця ділянок, зведених за іменем
 *   ./pssmap -a               уся система + перевірка балансу
 */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* Забирає файл ОДНИМ read(): лише так знімок карти злагоджений.
   Не влізло — усе спочатку, з удвічі більшим буфером. */
static char *slurp(const char *path, size_t *out_len)
{
    size_t cap = 1u << 20;

    for (;;) {
        int fd = open(path, O_RDONLY | O_CLOEXEC);
        if (fd < 0)
            return NULL;                     /* ENOENT — процес уже помер */

        char *buf = malloc(cap);
        if (!buf) { close(fd); return NULL; }

        ssize_t n = read(fd, buf, cap - 1);
        int err = errno;
        close(fd);

        if (n >= 0 && (size_t)n < cap - 1) { /* влізло цілком */
            buf[n] = '\0';
            *out_len = (size_t)n;
            return buf;
        }
        free(buf);

        if (n < 0) {                         /* ESRCH — помер посеред читання */
            if (err != EINTR) { errno = err; return NULL; }
            continue;                        /* сигнал: той самий буфер, з нуля */
        }
        if (cap >= (256u << 20)) { errno = EFBIG; return NULL; }
        cap *= 2;
    }
}
