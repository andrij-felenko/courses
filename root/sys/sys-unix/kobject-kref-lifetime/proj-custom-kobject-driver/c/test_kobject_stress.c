// test_kobject_stress.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <string.h>
#include <stdbool.h>

#define SYSFS_PATH "/sys/kernel/sample_device/baud_rate"
#define THREAD_COUNT 8

static volatile bool running = true;

static void *reader_thread(void *arg)
{
    long id = (long)arg;
    char buffer[64];

    while (running) {
        int fd = open(SYSFS_PATH, O_RDONLY);
        if (fd < 0) {
            // Файл видалено ядром під час вивантаження модуля
            usleep(1000);
            continue;
        }

        ssize_t bytes = read(fd, buffer, sizeof(buffer) - 1);
        if (bytes > 0) {
            buffer[bytes] = '\0';
        }
        close(fd);
        usleep(500);
    }
    return NULL;
}

static void *writer_thread(void *arg)
{
    const char *values[] = {"9600", "19200", "38400", "57600", "115200", "230400"};
    int idx = 0;

    while (running) {
        int fd = open(SYSFS_PATH, O_WRONLY);
        if (fd >= 0) {
            const char *val = values[idx % 6];
            write(fd, val, strlen(val));
            close(fd);
            idx++;
        }
        usleep(1000);
    }
    return NULL;
}

int main(void)
{
    pthread_t threads[THREAD_COUNT];
    printf("[STRESS] Запуск %d потоків читання/запису до %s\n", THREAD_COUNT, SYSFS_PATH);

    for (long i = 0; i < THREAD_COUNT - 1; i++) {
        pthread_create(&threads[i], NULL, reader_thread, (void *)i);
    }
    pthread_create(&threads[THREAD_COUNT - 1], NULL, writer_thread, NULL);

    printf("[STRESS] Тест активний. Виконайте 'rmmod sample_kobject_module' в іншому терміналі.\n");
    printf("[STRESS] Очікування 10 секунд...\n");
    sleep(10);

    running = false;
    for (int i = 0; i < THREAD_COUNT; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("[STRESS] Тест завершено без збоїв системи.\n");
    return 0;
}
