#define _GNU_SOURCE
#include <malloc.h>
#include <stdio.h>

int main(void) {
    /* Має сенс до того, як програма розгалузиться на потоки:
       вже створені арени це не прибирає.                     */
    if (!mallopt(M_ARENA_MAX, 2))
        fprintf(stderr, "mallopt(M_ARENA_MAX) не вдався\n");

    void *p = malloc(100);
    printf("просив 100, придатних %zu\n", malloc_usable_size(p));

    void **v = malloc(200000 * sizeof *v);
    for (int i = 0; i < 200000; i++) v[i] = malloc(512);
    for (int i = 0; i < 200000; i++) free(v[i]);
    free(v);

    struct mallinfo2 m = mallinfo2();
    printf("узято %zu, зайнято %zu, вільно всередині %zu, можна віддати %zu\n",
           m.arena, m.uordblks, m.fordblks, m.keepcost);

    printf("malloc_trim → %d\n", malloc_trim(0));
    malloc_stats();            /* у stderr */
    malloc_info(0, stdout);    /* XML у stdout */
    free(p);
    return 0;
}
