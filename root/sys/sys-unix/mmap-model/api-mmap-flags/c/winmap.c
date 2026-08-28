/* winmap.c — відобразити вікно файлу, що починається з довільного зсуву
 *   cc -O2 -Wall -o winmap winmap.c && ./winmap файл 9000 4000
 * Файл мусить бути щонайменше offset+length завдовжки: запис за кінець
 * файлу через відображення дає SIGBUS, а не подовжує файл.
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

struct window {
    void          *base;      /* що віддавати в munmap */
    size_t         map_len;   /* і з якою довжиною     */
    unsigned char *p;         /* а це вже потрібний байт */
};

static int window_open(struct window *w, const char *path, off_t off, size_t len)
{
    long   ps       = sysconf(_SC_PAGE_SIZE);
    off_t  base_off = off & ~((off_t)ps - 1);      /* униз до межі сторінки */
    size_t delta    = (size_t)(off - base_off);

    /* саме O_RDWR: MAP_SHARED разом із PROT_WRITE на O_RDONLY чи O_WRONLY
       дає EACCES — у першому випадку бракує права писати у файл,
       у другому ядру нізвідки взяти сторінку при першому збої */
    int fd = open(path, O_RDWR);
    if (fd < 0)
        return -1;

    w->map_len = len + delta;
    w->base    = mmap(NULL, w->map_len, PROT_READ | PROT_WRITE,
                      MAP_SHARED, fd, base_off);
    close(fd);                          /* ділянка тримає файл сама */
    if (w->base == MAP_FAILED)          /* саме MAP_FAILED, не NULL */
        return -1;

    w->p = (unsigned char *)w->base + delta;
    return 0;
}

int main(int argc, char **argv)
{
    if (argc != 4) {
        fprintf(stderr, "вжиток: %s файл зсув довжина\n", argv[0]);
        return 2;
    }
    off_t  off = strtoll(argv[2], NULL, 0);
    size_t len = strtoull(argv[3], NULL, 0);

    struct window w;
    if (window_open(&w, argv[1], off, len) < 0) { perror("window_open"); return 1; }

    memset(w.p, 'x', len);              /* звичайний запис у пам'ять */

    /* довговічність — окремим проханням, і саме від base */
    if (msync(w.base, w.map_len, MS_SYNC) < 0) perror("msync");
    if (munmap(w.base, w.map_len) < 0)         perror("munmap");
    return 0;
}
