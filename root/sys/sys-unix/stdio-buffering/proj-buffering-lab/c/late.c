/* late.c — запуск: strace -e trace=write -o late.txt ./late > /dev/null */
#include <stdio.h>

static char mine[64];            /* статичний: мусить пережити потік */

int main(void)
{
    printf("A: already in the buffer\n");

    int r = setvbuf(stdout, NULL, _IOLBF, 64);
    fprintf(stderr, "setvbuf -> %d\n", r);

    printf("B: goes out on the newline\n");

    setvbuf(stdout, mine, _IOFBF, sizeof mine);
    for (int i = 0; i < 8; i++)
        printf("filler line %d\n", i);

    return 0;
}
