// nvme_peek.c — читаємо перші 16 байтів NVMe-диска як звичайного файлу
// збірка:  gcc nvme_peek.c -o nvme_peek
// запуск:  sudo ./nvme_peek   (сирий диск читає лише root)
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#define DISK  "/dev/nvme0n1"   // весь диск; розділ був би nvme0n1p1

int main(void)
{
    // O_RDONLY — тільки читаємо; писати в сирий диск наосліп НЕБЕЗПЕЧНО
    int fd = open(DISK, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "не відкрив %s: %s\n", DISK, strerror(errno));
        return 1;
    }

    unsigned char buf[16];
    ssize_t n = read(fd, buf, sizeof buf);   // читаємо з початку диска
    if (n < 0) {
        fprintf(stderr, "читання не вдалось: %s\n", strerror(errno));
        close(fd);
        return 1;
    }

    printf("перші %zd байтів %s:\n", n, DISK);
    for (ssize_t i = 0; i < n; i++)
        printf("%02X ", buf[i]);
    printf("\n");

    close(fd);
    return 0;
}
