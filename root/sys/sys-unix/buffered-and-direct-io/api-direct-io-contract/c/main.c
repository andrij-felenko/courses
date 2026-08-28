#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/stat.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* 0 у mem — прямого обміну на цьому файлі немає. */
struct dio_align { unsigned mem, off; };

static void dio_query(int fd, struct dio_align *a)
{
    struct statx stx;
    a->mem = a->off = 4096;                       /* безпечне припущення */

    if (statx(fd, "", AT_EMPTY_PATH, STATX_DIOALIGN, &stx) != 0)
        return;                                   /* ядро < 4.11 */
    if (!(stx.stx_mask & STATX_DIOALIGN))
        return;                                   /* ядро < 6.1 або ФС мовчить */

    a->mem = stx.stx_dio_mem_align;               /* 0 — прямого обміну немає */
    a->off = stx.stx_dio_offset_align;
}

/* Кладе в out до len байтів з позиції pos. Повертає, скільки поклав. */
ssize_t dio_pread(int fd, void *out, size_t len, off_t pos,
                  struct dio_align a)
{
    if (a.off == 0) return -1;                    /* прямого обміну на файлі немає */

    size_t page  = (size_t)sysconf(_SC_PAGESIZE);
    size_t align = a.mem > page ? a.mem : page;   /* ≥ sizeof(void*), ≥ сторінки */

    off_t  first = pos - (pos % a.off);                       /* униз до межі */
    off_t  last  = ((pos + (off_t)len + a.off - 1) / a.off) * a.off;
    size_t span  = (size_t)(last - first);

    void *buf;
    if (posix_memalign(&buf, align, span) != 0)   /* код помилки — значенням */
        return -1;

    ssize_t got = pread(fd, buf, span, first);    /* EINVAL — вирівнювання */
    if (got < 0) { free(buf); return -1; }

    size_t skip = (size_t)(pos - first);
    if ((size_t)got <= skip) { free(buf); return 0; }   /* усе за кінцем файлу */

    size_t have = (size_t)got - skip;
    if (have > len) have = len;
    memcpy(out, (char *)buf + skip, have);
    free(buf);
    return (ssize_t)have;
}
