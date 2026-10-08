#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <stdint.h>

struct sample_packet {
    int16_t accel[3];
    int16_t pad;
    int64_t timestamp_ns;
};

int main(void) {
    int fd = open("/dev/iio:device0", O_RDONLY | O_NONBLOCK);
    if (fd < 0) {
        perror("Не вдалося відкрити пристрій в неблокуючому режимі");
        return EXIT_FAILURE;
    }

    struct pollfd pfd = { .fd = fd, .events = POLLIN };
    struct sample_packet sample;
    int64_t last_ts = 0;

    for (int i = 0; i < 20; ++i) {
        int poll_res = poll(&pfd, 1, 1000);
        if (poll_res < 0) {
            if (errno == EINTR) continue;
            perror("Помилка poll()");
            break;
        } else if (poll_res == 0) {
            fprintf(stderr, "Попередження: таймаут очікування даних IIO\n");
            continue;
        }

        ssize_t ret = read(fd, &sample, sizeof(sample));
        if (ret < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) continue;
            perror("Помилка читання");
            break;
        }

        if (last_ts != 0) {
            int64_t dt = sample.timestamp_ns - last_ts;
            if (dt > 20000000LL) {
                fprintf(stderr, "Виявлено втрату вибірок! dt = %lld ns\n", (long long)dt);
            }
        }
        last_ts = sample.timestamp_ns;
    }

    close(fd);
    return EXIT_SUCCESS;
}
