#define _XOPEN_SOURCE 600
#include <fcntl.h>
#include <stdio.h>

int main(void) {
    int fd = open("index.db", O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }

    /* Читатимемо навмання: вікна лише шкодять. */
    posix_fadvise(fd, 0, 0, POSIX_FADV_RANDOM);

    /* А цю ділянку точно прочитаємо всю — хай приїде заздалегідь. */
    posix_fadvise(fd, 4096 * 1024, 8192 * 1024, POSIX_FADV_WILLNEED);

    /* ... робота з файлом ... */
    close(fd);
    return 0;
}
