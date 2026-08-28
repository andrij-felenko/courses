/* fdchild.c — програма-нащадок: друкує свою таблицю дескрипторів
 * і перевіряє номери, названі в аргументах.
 *
 *   gcc -Wall -Wextra -O2 -o fdchild fdchild.c
 */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    DIR *d = opendir("/proc/self/fd");
    if (d == NULL) { perror("opendir"); return 1; }
    int own = dirfd(d);

    int fds[256], n = 0;
    struct dirent *e;
    while ((e = readdir(d)) != NULL && n < 256) {
        if (e->d_name[0] == '.') continue;
        int fd = (int)strtol(e->d_name, NULL, 10);
        if (fd != own) fds[n++] = fd;
    }
    closedir(d);

    for (int i = 0; i < n; i++) {
        char path[64], target[512];
        snprintf(path, sizeof path, "/proc/self/fd/%d", fds[i]);
        ssize_t len = readlink(path, target, sizeof target - 1);
        if (len < 0) len = 0;
        target[len] = '\0';
        fprintf(stderr, "[нащадок] %d -> %s\n", fds[i], target);
    }

    for (int i = 1; i < argc; i++) {
        int fd = (int)strtol(argv[i], NULL, 10);
        errno = 0;
        int alive = fcntl(fd, F_GETFD) >= 0;
        fprintf(stderr, "[нащадок] переданий номер %s: %s\n",
                argv[i], alive ? "живий" : strerror(errno));
    }

    printf("[нащадок] цей рядок пішов у номер 1\n");
    fflush(stdout);
    return 0;
}
