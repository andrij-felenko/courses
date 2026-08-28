/* y2038-fs.c — чи витримує ця файлова система дату за 2038 роком.
   Збирати ОБОВ'ЯЗКОВО з -D_FILE_OFFSET_BITS=64 -D_TIME_BITS=64.  */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define BEYOND 2177452800LL          /* 2039-01-01 00:00:00 UTC */
#define WALL   2147483647LL          /* 2038-01-19 03:14:07 UTC */

int main(int argc, char **argv)
{
    const char *dir = (argc > 1) ? argv[1] : ".";
    char path[4096];
    struct timespec times[2];
    struct stat st;
    long long got;
    int fd;

    if (sizeof(times[0].tv_sec) < 8) {
        fprintf(stderr, "tv_sec тут має %zu байти — перезберіть програму\n",
                sizeof(times[0].tv_sec));
        return 2;
    }

    snprintf(path, sizeof path, "%s/y2038probe.XXXXXX", dir);
    if ((fd = mkstemp(path)) < 0) { perror("mkstemp"); return 1; }

    times[0].tv_sec  = (time_t)BEYOND;    /* atime */
    times[0].tv_nsec = 123456789;
    times[1] = times[0];                  /* mtime */

    if (utimensat(AT_FDCWD, path, times, 0) != 0) { perror("utimensat"); goto out; }
    if (stat(path, &st) != 0)                     { perror("stat");      goto out; }

    got = (long long)st.st_mtim.tv_sec;
    printf("записано : %lld.%09ld\n", BEYOND, 123456789L);
    printf("прочитано: %lld.%09ld\n", got, (long)st.st_mtim.tv_nsec);

    if (got == BEYOND)
        puts("вердикт  : поле часу тут ширше за 32 біти");
    else if (got == WALL)
        puts("вердикт  : значення підрізано рівно до межі — поле 32-бітне");
    else
        printf("вердикт  : значення змінилося на %lld — розберіться окремо\n", got);

out:
    close(fd);
    unlink(path);
    return 0;
}
