#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/poll.h>

#define DEV_NODE "/dev/iio:device0"

// Бінарна структура кадру, що відповідає scan_type драйвера
struct __attribute__((packed)) iio_adc_frame {
    uint16_t raw_val;
    uint16_t pad[3];    // Паддінг для вирівнювання 64-бітного таймстампа
    int64_t timestamp;  // Таймстамп ядра у наносекундах
};

int main(void) {
    int fd = open(DEV_NODE, O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити " DEV_NODE);
        return EXIT_FAILURE;
    }

    struct pollfd pfd = { .fd = fd, .events = POLLIN };
    struct iio_adc_frame frame;

    printf("Очікування потокових даних від IIO...\n");
    for (int i = 0; i < 5; ++i) {
        int ret = poll(&pfd, 1, 3000);
        if (ret > 0 && (pfd.revents & POLLIN)) {
            ssize_t len = read(fd, &frame, sizeof(frame));
            if (len == sizeof(frame)) {
                printf("Семпл [%d]: RAW = %5u | Time = %lld ns\n",
                       i, frame.raw_val, (long long)frame.timestamp);
            }
        }
    }

    close(fd);
    return EXIT_SUCCESS;
}
