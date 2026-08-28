/* split-locks.c — скільки записів у ядрі коштує наша дисципліна замків. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static long kernel_locks(void)            /* усі замки системи, грубо */
{
    FILE *f = fopen("/proc/locks", "r");
    char line[256];
    long n = 0;
    while (fgets(line, sizeof line, f)) n++;
    fclose(f);
    return n;
}

int main(void)
{
    struct flock fl = { .l_type = F_WRLCK, .l_whence = SEEK_SET,
                        .l_start = 0, .l_len = 0 };
    int fd = open("/var/tmp/split.bin", O_RDWR | O_CREAT | O_TRUNC, 0644);
    off_t i;

    ftruncate(fd, 1 << 20);
    fcntl(fd, F_SETLK, &fl);              /* ОДНА заявка на весь файл */
    printf("одна заявка:        %ld записів у /proc/locks\n", kernel_locks());

    for (i = 1; i < 2000; i += 2) {       /* знімаємо кожен другий байт */
        struct flock hole = { .l_type = F_UNLCK, .l_whence = SEEK_SET,
                              .l_start = i, .l_len = 1 };
        if (fcntl(fd, F_SETLK, &hole) != 0) {
            printf("зупинилися на зміщенні %lld: %s\n",
                   (long long) i, strerror(errno));
            break;
        }
    }
    printf("після розрізання:   %ld записів у /proc/locks\n", kernel_locks());
    return 0;
}
