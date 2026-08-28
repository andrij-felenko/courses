#include <unistd.h>
#include <stdio.h>

int main(void) {
    void *before = sbrk(0);              /* нуль — просто прочитати межу */
    void *chunk  = sbrk(64 * 1024);      /* посунути вгору, отримати старе значення */
    void *after  = sbrk(0);

    printf("брейк %p → %p, ділянка від %p\n", before, after, chunk);

    sbrk(-64 * 1024);                    /* і назад */
    return 0;
}
