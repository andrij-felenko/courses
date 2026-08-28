#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <errno.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/loop0";

    // 1. Відкриття блочного пристрою у режимі O_DIRECT (обхід сторінкового кешу)
    int fd = open(dev_path, O_RDONLY | O_DIRECT);
    if (fd < 0) {
        fprintf(stderr, "Не вдалося відкрити блочний пристрій %s: %s\n", 
                dev_path, strerror(errno));
        return EXIT_FAILURE;
    }

    uint64_t disk_size_bytes = 0;
    int sector_size = 0;

    // 2. Запит параметрів блочного пристрою через ioctl
    if (ioctl(fd, BLKGETSIZE64, &disk_size_bytes) < 0) {
        perror("Помилка ioctl(BLKGETSIZE64)");
        close(fd);
        return EXIT_FAILURE;
    }

    if (ioctl(fd, BLKSSZGET, &sector_size) < 0) {
        perror("Помилка ioctl(BLKSSZGET)");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Пристрій: %s\n", dev_path);
    printf("Розмір диска: %" PRIu64 " байтів\n", disk_size_bytes);
    printf("Розмір логічного сектора: %d байтів\n", sector_size);

    // 3. Виділення вирівняної пам'яті для O_DIRECT через posix_memalign
    void *aligned_buf = NULL;
    size_t read_size = (size_t)sector_size * 2; // Читаємо 2 сектори
    
    if (posix_memalign(&aligned_buf, sector_size, read_size) != 0) {
        fprintf(stderr, "Помилка виділення вирівняної пам'яті за межею %d B\n", sector_size);
        close(fd);
        return EXIT_FAILURE;
    }

    // 4. Позиціонування на сектор 0 (кратне sector_size)
    if (lseek(fd, 0, SEEK_SET) < 0) {
        perror("Помилка позиціонування lseek");
        free(aligned_buf);
        close(fd);
        return EXIT_FAILURE;
    }

    // 5. Виконання прямого читання без залучення сторінкового кешу
    ssize_t bytes_read = read(fd, aligned_buf, read_size);
    if (bytes_read < 0) {
        fprintf(stderr, "Помилка O_DIRECT читання bdev: %s (код %d)\n", 
                strerror(errno), errno);
        free(aligned_buf);
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Успішно прочитано %zd байтів через O_DIRECT без кешування!\n", bytes_read);

    // 6. Очищення ресурсів
    free(aligned_buf);
    close(fd);
    return EXIT_SUCCESS;
}
