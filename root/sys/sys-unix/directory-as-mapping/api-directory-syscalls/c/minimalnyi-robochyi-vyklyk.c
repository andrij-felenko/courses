#define _GNU_SOURCE
#include <dirent.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    const char *path = (argc > 1) ? argv[1] : ".";

    int fd = open(path, O_RDONLY | O_DIRECTORY);
    if (fd < 0) { perror("open"); return 1; }

    _Alignas(8) char buf[64 * 1024];   /* вирівняно: у записах є 8-байтові поля */

    for (;;) {
        ssize_t n = getdents64(fd, buf, sizeof buf);
        if (n < 0) { perror("getdents64"); close(fd); return 1; }
        if (n == 0) break;             /* каталог вичерпано */

        for (ssize_t off = 0; off < n; ) {
            struct dirent64 *e = (struct dirent64 *)(buf + off);
            printf("%-10llu тип %-3u %s\n",
                   (unsigned long long)e->d_ino, (unsigned)e->d_type, e->d_name);
            off += e->d_reclen;        /* ЄДИНИЙ правильний крок */
        }
    }

    close(fd);
    return 0;
}
