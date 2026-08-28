#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>

static volatile sig_atomic_t keep_running = 1;

static void handle_sigint(int sig) {
    (void)sig;
    keep_running = 0;
}

static int write_sysfs(const char *path, const char *value) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        return -1;
    }
    ssize_t written = write(fd, value, strlen(value));
    close(fd);
    return written >= 0 ? 0 : -1;
}

int main(void) {
    const char *event_enable = "/sys/kernel/tracing/events/sample_subsys/sample_sensor_read/enable";
    const char *event_filter = "/sys/kernel/tracing/events/sample_subsys/sample_sensor_read/filter";
    const char *trace_pipe   = "/sys/kernel/tracing/trace_pipe";

    signal(SIGINT, handle_sigint);
    signal(SIGTERM, handle_sigint);

    printf("Налаштування ftrace для власної точки трасування...\n");

    /* 1. Встановлення предикату фільтрації */
    if (write_sysfs(event_filter, "raw_value > 40") != 0) {
        fprintf(stderr, "Помилка встановлення фільтра. Чи завантажено модуль tp_sample_mod?\n");
        return 1;
    }

    /* 2. Активація точки трасування */
    if (write_sysfs(event_enable, "1") != 0) {
        fprintf(stderr, "Помилка активації точки трасування\n");
        return 1;
    }

    /* 3. Читання безперервного потоку подій */
    int pipe_fd = open(trace_pipe, O_RDONLY);
    if (pipe_fd < 0) {
        perror("Не вдалося відкрити trace_pipe (потрібні права root)");
        write_sysfs(event_enable, "0");
        return 1;
    }

    printf("Очікування подій (фільтр: raw_value > 40)... Натисніть Ctrl+C для зупинки.\n");
    char buffer[512];

    while (keep_running) {
        ssize_t bytes = read(pipe_fd, buffer, sizeof(buffer) - 1);
        if (bytes > 0) {
            buffer[bytes] = '\0';
            printf("%s", buffer);
        } else if (bytes < 0 && errno != EINTR) {
            perror("Помилка читання з trace_pipe");
            break;
        }
    }

    /* 4. Відновлення вихідного стану системи */
    printf("\nЗупинка трасування та скидання фільтрів...\n");
    close(pipe_fd);
    write_sysfs(event_enable, "0");
    write_sysfs(event_filter, "0");

    return 0;
}
