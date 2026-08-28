/* hog.c — брати пам'ять по 8 МіБ і торкатися кожної сторінки.
   Списання відбувається саме на доторку, а не на malloc.
   збірка: cc -O2 -o hog hog.c                                        */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void)
{
    const long chunk = 8L << 20;              /* 8 МіБ */
    long page = sysconf(_SC_PAGESIZE), took = 0;

    for (;;) {
        char *p = malloc(chunk);
        if (!p) { fprintf(stderr, "malloc відмовив на %ld МіБ\n", took); return 1; }
        for (long i = 0; i < chunk; i += page)
            p[i] = 1;                         /* доторк = сторінка списана на групу */
        took += chunk >> 20;
        printf("%ld МіБ\n", took);
        fflush(stdout);
        usleep(50 * 1000);
    }
}
