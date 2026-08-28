/* firstwrite.c — скільки коштує намір писати у файл нижнього шару */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

static double now(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "вжиток: firstwrite <шлях> [trunc]\n"); return 2; }

    int flags = O_WRONLY;
    if (argc > 2 && strcmp(argv[2], "trunc") == 0) flags |= O_TRUNC;

    struct stat st;
    if (stat(argv[1], &st) < 0) { perror("stat"); return 1; }

    double t0 = now();
    int fd = open(argv[1], flags);       /* жодного байта не записано */
    double t1 = now();
    if (fd < 0) { perror("open"); return 1; }
    close(fd);

    double mib = st.st_size / 1048576.0, dt = t1 - t0;
    printf("open(%s%s): %.6f с при розмірі %.1f МіБ",
           argv[1], (flags & O_TRUNC) ? ", O_TRUNC" : "", dt, mib);
    /* швидкість має сенс лише там, де копіювання справді сталося */
    if (mib >= 1.0 && dt > 0.01) printf("  (%.0f МіБ/с)", mib / dt);
    printf("\n");
    return 0;
}
