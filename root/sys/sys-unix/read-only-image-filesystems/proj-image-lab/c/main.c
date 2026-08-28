#define _GNU_SOURCE
#define _FILE_OFFSET_BITS 64
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/resource.h>

/* /sys/block/<dev>/stat: поле 1 — читань, поле 3 — секторів по 512 Б */
static int read_stat(const char *path, unsigned long long *ios,
                     unsigned long long *sectors)
{
    FILE *f = fopen(path, "r");
    if (!f)
        return -1;
    unsigned long long a, b, c;
    int n = fscanf(f, "%llu %llu %llu", &a, &b, &c);
    fclose(f);
    if (n != 3)
        return -1;
    *ios = a;
    *sectors = c;
    return 0;
}

static off_t rnd_block(off_t span)          /* random() дає лише 31 біт */
{
    unsigned long long r = ((unsigned long long)random() << 31) ^ random();
    return (off_t)(r % (unsigned long long)span);
}

static double sys_seconds(void)
{
    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);
    return ru.ru_stime.tv_sec + ru.ru_stime.tv_usec / 1e6;
}

int main(int argc, char **argv)
{
    if (argc != 4) {
        fprintf(stderr, "вжиток: %s <файл-в-образі> <loopN> <читань>\n", argv[0]);
        return 2;
    }
    long iters = strtol(argv[3], NULL, 10);

    char statpath[128];
    snprintf(statpath, sizeof statpath, "/sys/block/%s/stat", argv[2]);

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }

    struct stat st;
    if (fstat(fd, &st) < 0) { perror("fstat"); return 1; }
    off_t span = st.st_size / 4096;
    if (span < 2) { fprintf(stderr, "файл замалий\n"); return 1; }

    /* найважливіший рядок: гасимо випереджувальне читання саме для цього файлу */
    posix_fadvise(fd, 0, 0, POSIX_FADV_RANDOM);

    unsigned long long ios0, sec0, ios1, sec1;
    if (read_stat(statpath, &ios0, &sec0) < 0) { perror(statpath); return 1; }
    double t0 = sys_seconds();

    char buf[4096];
    srandom(20260807);          /* та сама послідовність для всіх образів */
    unsigned long long got = 0;
    for (long i = 0; i < iters; i++) {
        ssize_t r = pread(fd, buf, sizeof buf, rnd_block(span) * 4096);
        if (r < 0) { perror("pread"); return 1; }
        got += (unsigned long long)r;
    }

    double t1 = sys_seconds();
    if (read_stat(statpath, &ios1, &sec1) < 0) { perror(statpath); return 1; }

    double from_dev = (sec1 - sec0) * 512.0;
    printf("віддано програмі : %llu Б\n", got);
    printf("запитів до %s : %llu\n", argv[2], ios1 - ios0);
    printf("прочитано з нього: %.0f Б\n", from_dev);
    printf("надлишок вводу   : ×%.1f\n", from_dev / (double)got);
    printf("розтискання      : %.3f с системного часу\n", t1 - t0);
    close(fd);
    return 0;
}
