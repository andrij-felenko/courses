/* y2038-probe.c — ширина типу часу й межа його шкали */
#define _GNU_SOURCE
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>

/* Максимум time_t, обчислений без жодного переповнення. */
static time_t time_t_max(void)
{
    if ((time_t)-1 > 0)                 /* тип виявився беззнаковим */
        return (time_t)-1;

    const unsigned bits = (unsigned)sizeof(time_t) * CHAR_BIT;
    return (time_t)(((uintmax_t)1 << (bits - 1)) - 1);
}

static void show(const char *what, time_t t)
{
    struct tm tm;
    char buf[64];

    /* gmtime_r віддає NULL, коли рік не влазить у int tm_year. */
    if (gmtime_r(&t, &tm) == NULL) {
        printf("%-14s %21jd   (у struct tm не вміщається)\n",
               what, (intmax_t)t);
        return;
    }
    strftime(buf, sizeof buf, "%Y-%m-%d %H:%M:%S UTC", &tm);
    printf("%-14s %21jd   %s\n", what, (intmax_t)t, buf);
}

int main(void)
{
    struct timespec now;
    time_t tmax = time_t_max();

    printf("sizeof(time_t)           = %zu\n", sizeof(time_t));
    printf("sizeof(struct timespec)  = %zu\n", sizeof(struct timespec));
    printf("sizeof(off_t)            = %zu\n", sizeof(off_t));
    printf("sizeof(st_mtim.tv_sec)   = %zu\n",
           sizeof(((struct stat *)0)->st_mtim.tv_sec));
    printf("sizeof(long)             = %zu\n", sizeof(long));
#ifdef __TIMESIZE
    printf("__TIMESIZE               = %d\n", __TIMESIZE);
#endif
#ifdef __USE_TIME_BITS64
    printf("64-бітний час            = увімкнено\n");
#endif
    putchar('\n');

    clock_gettime(CLOCK_REALTIME, &now);
    show("зараз", now.tv_sec);
    show("максимум", tmax);
    /* Перетворення завеликого беззнакового значення в знаковий тип стандарт
       лишає на розсуд реалізації — і GCC з Clang визначають його як
       загортання. Саме тому цей рядок писати можна, а «tmax + 1» — ні. */
    show("максимум + 1", (time_t)((uintmax_t)tmax + 1));
    return 0;
}
