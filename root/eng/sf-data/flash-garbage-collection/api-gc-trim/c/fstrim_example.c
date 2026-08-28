/* fstrim_example.c — Виклики FITRIM системним API у C */
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <errno.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <точка_монтування>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *mount_point = argv[1];
    int fd = open(mount_point, O_RDONLY | O_DIRECTORY);
    if (fd < 0) {
        perror("Помилка відкриття точки монтування");
        return EXIT_FAILURE;
    }

    struct fstrim_range range;
    memset(&range, 0, sizeof(range));
    range.start = 0;
    range.len = (uint64_t)-1; /* До кінця диска */
    range.minlen = 1024 * 1024; /* Мінімальний блок: 1 МБ */

    printf("Надсилання FITRIM для %s (minlen = %llu байтів)...\n", 
           mount_point, (unsigned long long)range.minlen);

    if (ioctl(fd, FITRIM, &range) < 0) {
        perror("Помилка виконання ioctl(FITRIM)");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Успішно! Звільнено накопичувачем: %llu байтів (%.2f МБ)\n",
           (unsigned long long)range.len,
           (double)range.len / (1024.0 * 1024.0));

    close(fd);
    return EXIT_SUCCESS;
}
