#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/ioctl.h>

struct __attribute__((packed)) iio_accel_sample {
    int16_t x;
    int16_t y;
    int16_t z;
    int16_t padding;
    int64_t timestamp;
};

int main(void) {
    const char *dev_path = "/dev/iio:device0";
    int fd = open(dev_path, O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити символьний пристрій IIO");
        return EXIT_FAILURE;
    }

    struct iio_accel_sample sample;
    printf("Очікування потоку вибірок з %s...\n", dev_path);

    for (int i = 0; i < 10; ++i) {
        ssize_t bytes_read = read(fd, &sample, sizeof(sample));
        if (bytes_read < 0) {
            perror("Помилка читання з буфера IIO");
            break;
        }
        if (bytes_read == sizeof(sample)) {
            printf("[%5d] X=%6d Y=%6d Z=%6d | Time: %lld ns\n",
                   i, sample.x, sample.y, sample.z, (long long)sample.timestamp);
        }
    }

    close(fd);
    return EXIT_SUCCESS;
}
