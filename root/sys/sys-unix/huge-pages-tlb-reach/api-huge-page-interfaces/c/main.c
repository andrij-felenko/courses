#define _GNU_SOURCE
#include <sys/mman.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

/* Узяти len байтів із пулу сторінок розміру 2^lg2. lg2 == 0 — розмір за домовленістю. */
static void *huge_alloc(size_t len, unsigned lg2)
{
        int flags = MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB
                  | (int)((lg2 & MAP_HUGE_MASK) << MAP_HUGE_SHIFT);

        void *p = mmap(NULL, len, PROT_READ | PROT_WRITE, flags, -1, 0);
        if (p == MAP_FAILED) {
                fprintf(stderr, "MAP_HUGETLB %zu Б: %s\n", len, strerror(errno));
                return NULL;
        }
        /* Резервування вже зроблено, але торкнутися варто тут, а не в гарячому шляху. */
        memset(p, 0, len);
        return p;
}

int main(void)
{
        void *p = huge_alloc(4ull << 30, 30);   /* чотири сторінки по 1 ГіБ */
        if (!p)
                return 1;
        printf("%p\n", p);
        return 0;
}
