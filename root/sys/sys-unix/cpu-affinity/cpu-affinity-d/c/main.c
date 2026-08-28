#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

int main(void) {
    cpu_set_t set;

    CPU_ZERO(&set);
    CPU_SET(3, &set);                     /* дозволяємо лише ядро 3 */

    if (sched_setaffinity(0, sizeof(set), &set) != 0) {
        fprintf(stderr, "sched_setaffinity: %s\n", strerror(errno));
        return 1;
    }

    /* повернення з виклику — уже гарантія: якщо задача бігла не там,
       ядро перенесло її на дозволене ядро ще всередині виклику */
    printf("біжу на ядрі %d\n", sched_getcpu());

    CPU_ZERO(&set);
    if (sched_getaffinity(0, sizeof(set), &set) == 0)
        printf("дозволено ядер: %d\n", CPU_COUNT(&set));

    return 0;
}
