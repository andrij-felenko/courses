#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>

static volatile sig_atomic_t g_stop = 0;

static void sig_handler(int sig) {
    (void)sig;
    g_stop = 1;
}

static int write_file(const char *path, const char *val) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        return -1;
    }
    ssize_t len = write(fd, val, strlen(val));
    close(fd);
    return (len == (ssize_t)strlen(val)) ? 0 : -1;
}

int main(void) {
    const char *enable_path = "/sys/kernel/tracing/events/syscalls/sys_enter_openat/enable";
    const char *filter_path = "/sys/kernel/tracing/events/syscalls/sys_enter_openat/filter";
    const char *pipe_path   = "/sys/kernel/tracing/trace_pipe";

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    printf("Ініціалізація трасування точки syscalls:sys_enter_openat...\n");

    /* 1. Фільтруємо системні виклики лише для сторонніх процесів */
    char filter_buf[128];
    snprintf(filter_buf, sizeof(filter_buf), "common_pid != %d", getpid());
    if (write_file(filter_path, filter_buf) != 0) {
        fprintf(stderr, "Перевірте права доступу (потрібен root) та наявність debugfs/tracefs\n");
        return 1;
    }

    /* 2. Активація точки трасування */
    if (write_file(enable_path, "1") != 0) {
        return 1;
    }

    /* 3. Відкриття потокового інтерфейсу */
    int pipe_fd = open(pipe_path, O_RDONLY);
    if (pipe_fd < 0) {
        perror("Помилка відкриття trace_pipe");
        write_file(enable_path, "0");
        return 1;
    }

    printf("Збір подій розпочато. Натисніть Ctrl+C для зупинки.\n");
    char line_buf[1024];

    while (!g_stop) {
        ssize_t bytes = read(pipe_fd, line_buf, sizeof(line_buf) - 1);
        if (bytes > 0) {
            line_buf[bytes] = '\0';
            printf("%s", line_buf);
        } else if (bytes < 0 && errno != EINTR) {
            perror("Помилка читання з trace_pipe");
            break;
        }
    }

    /* 4. Відновлення вихідного стану системи */
    printf("\nДеактивація трасування та очищення фільтрів...\n");
    close(pipe_fd);
    write_file(enable_path, "0");
    write_file(filter_path, "0");

    return 0;
}
