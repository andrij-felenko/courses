#define _GNU_SOURCE
#include <stdio.h>
#include <sys/mman.h>
#include <sys/resource.h>

int main(void) {
    struct rusage a, b;
    size_t len = 64UL << 20;                    /* 64 МіБ */

    getrusage(RUSAGE_SELF, &a);

    char *p = mmap(NULL, len, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) { perror("mmap"); return 1; }
    for (size_t i = 0; i < len; i += 4096) p[i] = 1;

    getrusage(RUSAGE_SELF, &b);
    printf("дрібних %ld, великих %ld\n",
           b.ru_minflt - a.ru_minflt, b.ru_majflt - a.ru_majflt);

    munmap(p, len);
    return 0;
}
