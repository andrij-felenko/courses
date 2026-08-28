#define _GNU_SOURCE
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/times.h>
#include <sys/resource.h>

static double cpu_seconds(clockid_t c)
{
    struct timespec t;
    if (clock_gettime(c, &t) != 0)
        return -1.0;
    return t.tv_sec + t.tv_nsec / 1e9;
}

int main(void)
{
    const double tck = (double)sysconf(_SC_CLK_TCK);   /* НЕ 100 напам'ять */

    /* 1. times() — тики USER_HZ; процес окремо, дочекані нащадки окремо */
    struct tms tm;
    errno = 0;
    if (times(&tm) == (clock_t)-1 && errno != 0) {
        perror("times");
        return 1;
    }
    printf("times    user %.2f  sys %.2f  нащадки %.2f\n",
           tm.tms_utime / tck, tm.tms_stime / tck,
           (tm.tms_cutime + tm.tms_cstime) / tck);

    /* 2. getrusage() — мікросекунди, той самий поділ, дрібніше решето */
    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);
    printf("rusage   user %.6f  sys %.6f\n",
           ru.ru_utime.tv_sec + ru.ru_utime.tv_usec / 1e6,
           ru.ru_stime.tv_sec + ru.ru_stime.tv_usec / 1e6);

    /* 3. процесорні годинники — наносекунди, точна сума без поділу */
    printf("clock    процес %.9f  потік %.9f\n",
           cpu_seconds(CLOCK_PROCESS_CPUTIME_ID),
           cpu_seconds(CLOCK_THREAD_CPUTIME_ID));

    /* 4. schedstat — наносекунди, але ЛИШЕ цей потік */
    unsigned long long run = 0, wait = 0;
    unsigned long slices = 0;
    FILE *f = fopen("/proc/self/schedstat", "r");
    if (f) {
        if (fscanf(f, "%llu %llu %lu", &run, &wait, &slices) == 3)
            printf("sched    на процесорі %.9f  у черзі %.9f  вибрано %lu разів\n",
                   run / 1e9, wait / 1e9, slices);
        fclose(f);
    }

    /* 5. /proc/self/stat — тики USER_HZ; comm може містити дужки й пробіли */
    char buf[4096];
    size_t n = 0;
    f = fopen("/proc/self/stat", "r");
    if (f) {
        n = fread(buf, 1, sizeof buf - 1, f);
        fclose(f);
    }
    buf[n] = '\0';

    char *p = strrchr(buf, ')');          /* кінець поля 2 */
    if (p) {
        unsigned long ut = 0, st = 0;
        /* p+2 — поле 3 (state); далі 5 int, 1 unsigned, 4 lu, і аж тоді 14 і 15 */
        if (sscanf(p + 2, "%*c %*d %*d %*d %*d %*d %*u %*lu %*lu %*lu %*lu %lu %lu",
                   &ut, &st) == 2)
            printf("stat     user %.2f  sys %.2f\n", ut / tck, st / tck);
    }
    return 0;
}
