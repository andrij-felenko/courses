/* dirtier.c — керований генератор брудних сторінок; cc -O2 -o dirtier dirtier.c */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BLK (1u << 20)                  /* 1 МіБ: кратний будь-якому логічному блоку */

int main(int argc, char **argv)
{
    if (argc < 4) {
        fprintf(stderr, "usage: %s <файл> <МіБ> buffered|direct"
                        " [fsync_кожні_МіБ] [зсув_МіБ]\n", argv[0]);
        return 2;
    }
    const char *path   = argv[1];
    long        mib    = atol(argv[2]);
    int         direct = strcmp(argv[3], "direct") == 0;
    long        every  = argc > 4 ? atol(argv[4]) : 0;
    long        start  = argc > 5 ? atol(argv[5]) : 0;

    int flags = O_WRONLY | O_CREAT | (direct ? O_DIRECT : 0);
    int fd = open(path, flags, 0644);
    if (fd < 0) { perror("open"); return 1; }
    if (lseek(fd, (off_t)start * BLK, SEEK_SET) < 0) { perror("lseek"); return 1; }

    void *buf;                          /* O_DIRECT вимагає вирівняного буфера */
    int rc = posix_memalign(&buf, 4096, BLK);          /* повертає код, а не ставить errno */
    if (rc) { fprintf(stderr, "posix_memalign: %s\n", strerror(rc)); return 1; }
    memset(buf, 0xA5, BLK);

    for (long i = 0; i < mib; i++) {
        for (size_t done = 0; done < BLK; ) {
            ssize_t n = write(fd, (char *)buf + done, BLK - done);
            if (n < 0) { perror("write"); return 1; }
            done += (size_t)n;
        }
        if (every && (i + 1) % every == 0 && fsync(fd) < 0) { perror("fsync"); return 1; }
    }
    if (close(fd) < 0) { perror("close"); return 1; }   /* тут спливають відкладені помилки */
    return 0;
}
