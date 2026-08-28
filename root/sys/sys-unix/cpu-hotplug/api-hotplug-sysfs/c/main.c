#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/sysinfo.h>
#include <unistd.h>

/* Порахувати номери в списку виду "0-5,7,9-15". Порожній рядок — це нуль. */
static long count_cpu_list(const char *s)
{
    long total = 0;

    while (*s) {
        char *end;
        long lo = strtol(s, &end, 10);
        if (end == s)                  /* не число — далі читати нічого */
            break;
        long hi = lo;
        s = end;

        if (*s == '-') {               /* відрізок */
            hi = strtol(s + 1, &end, 10);
            if (end == s + 1)
                break;
            s = end;
        }
        if (hi >= lo)
            total += hi - lo + 1;

        if (*s != ',')                 /* кінець рядка */
            break;
        s++;
    }
    return total;
}

static long read_cpu_list(const char *path)
{
    char buf[4096];
    FILE *f = fopen(path, "r");
    if (f == NULL)
        return -1;

    long n = fgets(buf, sizeof buf, f) ? count_cpu_list(buf) : 0;
    fclose(f);
    return n;
}

int main(void)
{
    long possible = read_cpu_list("/sys/devices/system/cpu/possible");
    long present  = read_cpu_list("/sys/devices/system/cpu/present");
    long online   = read_cpu_list("/sys/devices/system/cpu/online");
    long offline  = read_cpu_list("/sys/devices/system/cpu/offline");

    printf("possible %ld  present %ld  online %ld  offline %ld\n",
           possible, present, online, offline);
    printf("_SC_NPROCESSORS_CONF %ld  _SC_NPROCESSORS_ONLN %ld\n",
           sysconf(_SC_NPROCESSORS_CONF), sysconf(_SC_NPROCESSORS_ONLN));

    /* Набір рівно тієї ширини, яку обіцяє possible: номери 0 … possible-1. */
    if (possible < 1)
        possible = CPU_SETSIZE;

    size_t size = CPU_ALLOC_SIZE(possible);
    cpu_set_t *set = CPU_ALLOC(possible);
    if (set == NULL) {
        perror("CPU_ALLOC");
        return 1;
    }
    CPU_ZERO_S(size, set);

    if (sched_getaffinity(0, size, set) != 0) {
        perror("sched_getaffinity");   /* EINVAL тут = буфер замалий */
        return 1;
    }

    printf("дозволено нам %d, зараз біжимо на %d\n",
           CPU_COUNT_S(size, set), sched_getcpu());

    CPU_FREE(set);
    return 0;
}
