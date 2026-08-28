#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/counter.h>

/* Допоміжна функція для зчитування absolute count з sysfs при відновленні */
static long long read_sysfs_absolute_count(void)
{
    FILE *fp = fopen("/sys/bus/counter/devices/counter0/count0/count", "r");
    if (!fp) {
        perror("Не вдалося відкрити sysfs count для відновлення");
        return -1;
    }
    long long val = 0;
    if (fscanf(fp, "%lld", &val) != 1) {
        val = -1;
    }
    fclose(fp);
    return val;
}

int main(void)
{
    /* Крок 1. Відкриття символьного пристрою counter */
    int fd = open("/dev/counter0", O_RDWR);
    if (fd < 0) {
        perror("Помилка: не вдалося відкрити /dev/counter0");
        return EXIT_FAILURE;
    }

    /* Крок 2. Налаштування спостерігача за подією переповнення (OVERFLOW) */
    struct counter_watch watch_overflow = {
        .event = COUNTER_EVENT_OVERFLOW,
        .channel = 0,
        .component.type = COUNTER_COMPONENT_NONE,
    };

    if (ioctl(fd, COUNTER_ADD_WATCH_IOCTL, &watch_overflow) < 0) {
        perror("Помилка додавання watch OVERFLOW");
        close(fd);
        return EXIT_FAILURE;
    }

    /* Крок 3. Налаштування спостерігача за індексним сигналом Z (INDEX) */
    struct counter_watch watch_index = {
        .event = COUNTER_EVENT_INDEX,
        .channel = 0,
        .component.type = COUNTER_COMPONENT_NONE,
    };

    if (ioctl(fd, COUNTER_ADD_WATCH_IOCTL, &watch_index) < 0) {
        perror("Помилка додавання watch INDEX");
        close(fd);
        return EXIT_FAILURE;
    }

    /* Крок 4. Увімкнення генерації подій у ядрі */
    if (ioctl(fd, COUNTER_ENABLE_EVENTS_IOCTL) < 0) {
        perror("Помилка включення подій Counter");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Спостереження за подіями /dev/counter0 активовано. Очікування...\n");

    struct pollfd pfd = {
        .fd = fd,
        .events = POLLIN,
    };

    struct counter_event evbuf[8];
    unsigned long long last_timestamp = 0;
    unsigned long long last_value = 0;
    const double ppr = 4096.0; /* 4096 імпульсів на оберт */

    /* Крок 5. Основний подійний цикл (Event Loop) */
    for (int iter = 0; iter < 10; ++iter) {
        int ret = poll(&pfd, 1, 5000); /* Таймаут 5000 мс (5 секунд) */
        if (ret < 0) {
            if (errno == EINTR)
                continue; /* Переривання сигналом POSIX */
            perror("Помилка виклику poll()");
            break;
        }
        if (ret == 0) {
            printf("Таймаут очікування подій counter\n");
            continue;
        }

        if (pfd.revents & POLLIN) {
            ssize_t bytes_read = read(fd, evbuf, sizeof(evbuf));
            if (bytes_read < 0) {
                if (errno == EOVERFLOW) {
                    fprintf(stderr, "УВАГА: Відбулося переповнення буфера подій ядра (EOVERFLOW)!\n");
                    long long abs_val = read_sysfs_absolute_count();
                    fprintf(stderr, "Відновлення синхронізації: sysfs absolute count = %lld\n", abs_val);
                    last_timestamp = 0; /* Скидаємо часову мітку */
                    continue;
                }
                perror("Помилка читання з /dev/counter0");
                break;
            }

            size_t count = bytes_read / sizeof(struct counter_event);
            for (size_t i = 0; i < count; ++i) {
                printf("[Timestamp: %llu ns] Watch ID: %u | Value: %llu | Channel: %u\n",
                       (unsigned long long)evbuf[i].timestamp,
                       (unsigned int)evbuf[i].watch_id,
                       (unsigned long long)evbuf[i].value,
                       (unsigned int)evbuf[i].channel);

                /* Розрахунок кутової швидкості при наявності попередньої мітки */
                if (last_timestamp > 0 && evbuf[i].timestamp > last_timestamp) {
                    double dt_sec = (double)(evbuf[i].timestamp - last_timestamp) / 1e9;
                    double d_val = (double)(evbuf[i].value - last_value);
                    double rpm = (d_val / (ppr * 4.0)) / (dt_sec / 60.0);
                    printf("  -> Обчислена швидкість: %.2f RPM (dt = %.6f с)\n", rpm, dt_sec);
                }
                last_timestamp = evbuf[i].timestamp;
                last_value = evbuf[i].value;
            }
        }
    }

    close(fd);
    return EXIT_SUCCESS;
}
