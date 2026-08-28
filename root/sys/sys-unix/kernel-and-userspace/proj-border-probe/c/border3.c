/* border3.c — три секунди роботи й жодного перетину.  gcc -O2 -o border3 border3.c */
#include <stdio.h>

int main(void)
{
    volatile long s = 0;                  /* volatile, інакше -O2 викине цикл цілком */
    for (long i = 0; i < 1000000000L; i++) s += i;
    printf("%ld\n", s);
    return 0;
}
