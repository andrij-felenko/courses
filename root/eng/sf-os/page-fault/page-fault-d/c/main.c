#define _GNU_SOURCE
#include <stdio.h>
#include <time.h>
#include <sys/mman.h>
#include <sys/resource.h>

#define PGSZ  4096UL
#define LEN   (1024UL * 1024 * 1024)      /* 1 ГіБ */

static long minflt(void) {
    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);
    return ru.ru_minflt;
}

static double now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(void) {
    long f0 = minflt();
    double t0 = now();

    char *p = mmap(NULL, LEN, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) { perror("mmap"); return 1; }
    printf("запит:           %8.3f мс, збоїв %ld\n",
           (now() - t0) * 1e3, minflt() - f0);

    f0 = minflt(); t0 = now();
    for (size_t i = 0; i < LEN; i += PGSZ) p[i] = 1;
    double dt = now() - t0;
    long n = minflt() - f0;
    printf("перший дотик:    %8.3f мс, збоїв %ld, %.0f нс на збій\n",
           dt * 1e3, n, n ? dt * 1e9 / n : 0.0);

    f0 = minflt(); t0 = now();
    for (size_t i = 0; i < LEN; i += PGSZ) p[i] = 2;
    printf("другий прохід:   %8.3f мс, збоїв %ld\n",
           (now() - t0) * 1e3, minflt() - f0);

    munmap(p, LEN);
    return 0;
}
