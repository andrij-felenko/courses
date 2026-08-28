#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>

#define SECTOR_SIZE 4096

// Функція виконує безпечне відкриття, скидання та запис у файл-зону zonefs
int write_to_zone_c(const char *zone_file_path, const void *buffer, size_t len) {
    if (len % 512 != 0) {
        fprintf(stderr, "Розмір запису %zu не вирівняний на сектор 512B\n", len);
        return -EINVAL;
    }

    // Відкриваємо файл зони у режимі лише запис + O_APPEND (обов'язково для zonefs seq)
    int fd = open(zone_file_path, O_WRONLY | O_APPEND | O_DIRECT);
    if (fd < 0) {
        int err = errno;
        perror("Не вдалося відкрити файл зони zonefs");
        return -err;
    }

    // Скидання зони у стан Empty (WP -> Start LBA).
    // У zonefs truncate файлу до довжини 0 змушує ядро видати команду Reset Zone.
    if (ftruncate(fd, 0) < 0) {
        int err = errno;
        perror("Помилка виконання ftruncate(fd, 0) для скидання зони");
        close(fd);
        return -err;
    }

    // Дописування даних у зону. Ядро конвертує O_APPEND у команду Zone Append.
    ssize_t bytes_written = write(fd, buffer, len);
    if (bytes_written < 0) {
        int err = errno;
        perror("Помилка виконання write() через Zone Append");
        close(fd);
        return -err;
    }

    printf("[C] Успішно записано %zd байтів у зону %s\n", bytes_written, zone_file_path);

    close(fd);
    return 0;
}

int main(void) {
    void *buffer = NULL;
    // Для O_DIRECT потрібна вирівняна адреса пам'яті на межу сектора
    if (posix_memalign(&buffer, SECTOR_SIZE, SECTOR_SIZE) != 0) {
        perror("Помилка виділення вирівняної пам'яті");
        return EXIT_FAILURE;
    }

    memset(buffer, 0x5A, SECTOR_SIZE);

    const char *target_zone = "/mnt/zonefs/seq/0";
    int ret = write_to_zone_c(target_zone, buffer, SECTOR_SIZE);

    free(buffer);

    if (ret != 0) {
        fprintf(stderr, "[C] Операцію запису завершено з помилкою %d\n", ret);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
