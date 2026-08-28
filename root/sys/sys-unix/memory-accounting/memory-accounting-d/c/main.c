#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>

#define GIB  (1024UL * 1024 * 1024)
#define PGSZ 4096UL

static void report(const char *label)
{
    unsigned long size, resident, shared;
    FILE *f = fopen("/proc/self/statm", "r");
    if (!f || fscanf(f, "%lu %lu %lu", &size, &resident, &shared) != 3) {
        perror("statm");
        exit(1);
    }
    fclose(f);
    printf("%-26s VSZ = %5lu МіБ   RSS = %4lu МіБ\n", label,
           size * PGSZ / (1024 * 1024), resident * PGSZ / (1024 * 1024));
}

int main(void)
{
    report("на старті");

    char *p = mmap(NULL, GIB, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) { perror("mmap"); return 1; }
    report("після mmap 1 ГіБ");

    for (unsigned long off = 0; off < GIB / 4; off += PGSZ)
        p[off] = 1;                          /* по одному байту на сторінку */
    report("після запису в 256 МіБ");

    madvise(p, GIB / 4, MADV_DONTNEED);      /* кадри — назад ядру */
    report("після madvise(DONTNEED)");

    munmap(p, GIB);
    report("після munmap");
    return 0;
}
