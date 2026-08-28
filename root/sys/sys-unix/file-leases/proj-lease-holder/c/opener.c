/* opener.c — скільки коштує відкрити орендований файл.
 * gcc -O2 -Wall -o opener opener.c
 * ./opener /tmp/leased.dat [w] [n]   w — на запис, n — з O_NONBLOCK    */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    int flags = O_RDONLY;
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "w")) flags = (flags & ~O_ACCMODE) | O_WRONLY;
        if (!strcmp(argv[i], "n")) flags |= O_NONBLOCK;
    }
    struct timespec a, b;
    clock_gettime(CLOCK_MONOTONIC, &a);
    int fd = open(argv[1], flags);
    int e = errno;
    clock_gettime(CLOCK_MONOTONIC, &b);
    printf("open: %s, %.1f мс\n", fd < 0 ? strerror(e) : "успіх",
           (b.tv_sec - a.tv_sec) * 1e3 + (b.tv_nsec - a.tv_nsec) / 1e6);
    if (fd >= 0) close(fd);
    return 0;
}
