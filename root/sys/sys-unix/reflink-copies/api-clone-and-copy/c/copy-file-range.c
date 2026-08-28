#define _GNU_SOURCE
#define _FILE_OFFSET_BITS 64
#include <unistd.h>
#include <errno.h>

/* Копіює len байтів від початку fd_in у початок fd_out. 0 або -1 з errno. */
int copy_all(int fd_in, int fd_out, off_t len)
{
    off_t in_off = 0, out_off = 0;

    while (len > 0) {
        ssize_t n = copy_file_range(fd_in, &in_off, fd_out, &out_off,
                                    (size_t)len, 0);
        if (n < 0)
            return -1;              /* errno вже виставлено */
        if (n == 0) {               /* джерело скінчилося раніше, ніж чекали */
            errno = EIO;
            return -1;
        }
        len -= n;                   /* in_off і out_off ядро посунуло само */
    }
    return 0;
}
