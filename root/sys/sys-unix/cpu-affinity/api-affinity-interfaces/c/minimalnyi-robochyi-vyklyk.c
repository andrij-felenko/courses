#define _GNU_SOURCE
#include <errno.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>

/* Набір рівно того розміру, якого хоче ядро цієї машини.
   Розміру наперед не знаємо, тому подвоюємо, доки виклик відмовляє. */
static cpu_set_t *affinity_set_alloc(size_t *out_size)
{
    for (int ncpu = CPU_SETSIZE; ncpu <= (1 << 20); ncpu *= 2) {
        cpu_set_t *set = CPU_ALLOC(ncpu);
        if (set == NULL)
            return NULL;                       /* errno вже від malloc */

        size_t size = CPU_ALLOC_SIZE(ncpu);
        CPU_ZERO_S(size, set);

        if (sched_getaffinity(0, size, set) == 0) {
            *out_size = size;
            return set;
        }

        CPU_FREE(set);
        if (errno != EINVAL)                   /* тут EINVAL = «буфер замалий» */
            return NULL;
    }
    errno = EOVERFLOW;
    return NULL;
}

int main(void)
{
    size_t size;
    cpu_set_t *allowed = affinity_set_alloc(&size);
    if (allowed == NULL) {
        perror("sched_getaffinity");
        return 1;
    }

    printf("дозволено ядер: %d\n", CPU_COUNT_S(size, allowed));

    int chosen = -1;
    for (int cpu = 0; cpu < (int)(size * 8); cpu++)
        if (CPU_ISSET_S(cpu, size, allowed)) { chosen = cpu; break; }

    if (chosen < 0) {                          /* так не буває, але перевірити дешево */
        fprintf(stderr, "маска порожня\n");
        return 1;
    }

    cpu_set_t *one = CPU_ALLOC((int)(size * 8));
    if (one == NULL) {
        perror("CPU_ALLOC");
        return 1;
    }
    CPU_ZERO_S(size, one);
    CPU_SET_S(chosen, size, one);

    if (sched_setaffinity(0, size, one) != 0) {
        switch (errno) {
        case EINVAL: fprintf(stderr, "ядро %d цій задачі не належить\n", chosen); break;
        case EPERM:  fprintf(stderr, "немає права міняти маску\n");                break;
        default:     perror("sched_setaffinity");
        }
        return 1;
    }

    printf("прив'язано до %d, біжу на %d\n", chosen, sched_getcpu());

    CPU_FREE(one);
    CPU_FREE(allowed);
    return 0;
}
