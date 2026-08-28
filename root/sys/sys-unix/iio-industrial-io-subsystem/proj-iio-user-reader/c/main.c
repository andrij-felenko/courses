#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <errno.h>
#include <sys/poll.h>

#define SYSFS_PATH "/sys/bus/iio/devices/iio:device0"
#define DEV_PATH   "/dev/iio:device0"

static int write_sysfs_int(const char *path, int val) {
    char buf[32];
    int fd = open(path, O_WRONLY);
    if (fd < 0) return -errno;

    int len = snprintf(buf, sizeof(buf), "%d\n", val);
    ssize_t ret = write(fd, buf, len);
    close(fd);
    return (ret == len) ? 0 : -EIO;
}

static int write_sysfs_str(const char *path, const char *str) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) return -errno;

    size_t len = strlen(str);
    ssize_t ret = write(fd, str, len);
    close(fd);
    return (ret == (ssize_t)len) ? 0 : -EIO;
}

// Структура кадру: 16-біт відлік АЦП + 6-байтний паддінг + 64-бітний таймстамп
struct __attribute__((packed)) iio_sample_frame {
    uint16_t raw_value;
    uint16_t padding[3];
    int64_t timestamp_ns;
};

int main(void) {
    printf("Ініціалізація та налаштування кільцевого буфера IIO...\n");

    // 1. Деактивувати буфер перед конфігурацією
    write_sysfs_int(SYSFS_PATH "/buffer/enable", 0);

    // 2. Увімкнути перший канал напруги та системний таймстамп
    if (write_sysfs_int(SYSFS_PATH "/scan_elements/in_voltage0_en", 1) < 0) {
        perror("Помилка включення scan_elements/in_voltage0_en");
        return EXIT_FAILURE;
    }
    write_sysfs_int(SYSFS_PATH "/scan_elements/in_timestamp_en", 1);

    // 3. Встановити розмір кільцевого буфера kfifo
    write_sysfs_int(SYSFS_PATH "/buffer/length", 128);

    // 4. Встановити вотермарк для зменшення кількості розбуджень
    write_sysfs_int(SYSFS_PATH "/buffer/watermark", 16);

    // 5. Активувати буфер ядра
    if (write_sysfs_int(SYSFS_PATH "/buffer/enable", 1) < 0) {
        perror("Помилка активації buffer/enable");
        return EXIT_FAILURE;
    }

    // 6. Відкрити символьний пристрій для читання бінарних семплів
    int dev_fd = open(DEV_PATH, O_RDONLY);
    if (dev_fd < 0) {
        perror("Помилка відкриття файлу " DEV_PATH);
        write_sysfs_int(SYSFS_PATH "/buffer/enable", 0);
        return EXIT_FAILURE;
    }

    struct pollfd pfd = { .fd = dev_fd, .events = POLLIN };
    struct iio_sample_frame frame;

    printf("Розпочато зчитування семплів із пристрою " DEV_PATH "...\n");
    for (int i = 0; i < 10; ++i) {
        int poll_ret = poll(&pfd, 1, 5000); // 5 секунд таймаут
        if (poll_ret <= 0) {
            fprintf(stderr, "Таймаут або помилка системного виклику poll()\n");
            break;
        }

        ssize_t bytes = read(dev_fd, &frame, sizeof(frame));
        if (bytes == sizeof(frame)) {
            printf("[%d] RAW: %5u | Timestamp: %lld ns\n",
                   i, frame.raw_value, (long long)frame.timestamp_ns);
        } else {
            fprintf(stderr, "Помилка читання: прочитано %zd байт замість %zu\n",
                    bytes, sizeof(frame));
        }
    }

    // Деактивація та чистка ресурсів
    close(dev_fd);
    write_sysfs_int(SYSFS_PATH "/buffer/enable", 0);
    printf("Збір даних завершено успішно.\n");
    return EXIT_SUCCESS;
}
