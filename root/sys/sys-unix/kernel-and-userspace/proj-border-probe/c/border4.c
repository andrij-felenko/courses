/* border4.c — 65 536 перетинів межі, яких strace не покаже.  gcc -O2 -o border4 border4.c */
#define _GNU_SOURCE
#include <stdio.h>
#include <sys/mman.h>
#include <sys/resource.h>

int main(void)
{
    size_t len = 256u << 20;                              /* 256 МіБ */
    char *p = mmap(NULL, len, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);   /* один системний виклик */
    if (p == MAP_FAILED) { perror("mmap"); return 1; }

    struct rusage r0, r1;
    getrusage(RUSAGE_SELF, &r0);
    for (size_t i = 0; i < len; i += 4096) p[i] = 1;      /* торкаємося кожної сторінки */
    getrusage(RUSAGE_SELF, &r1);

    printf("дрібних збоїв %ld, великих %ld\n",
           r1.ru_minflt - r0.ru_minflt, r1.ru_majflt - r0.ru_majflt);
    return 0;
}
