#include <stdio.h>

void draw(int percent) {
    char bar[41];
    int filled = percent * 40 / 100;
    for (int i = 0; i < 40; i++)
        bar[i] = (i < filled) ? '#' : '.';
    bar[40] = '\0';

    /* \r          — каретку на початок рядка (це ще ASCII, не послідовність)
       ESC [ K     — стерти від курсора до кінця рядка
       ESC [ 32 m  — далі зелений, ESC [ 0 m — повернути звичайний */
    printf("\r\033[K[\033[32m%s\033[0m] %3d%%", bar, percent);
    fflush(stdout);   /* без цього рядок вийде не одразу */
}
