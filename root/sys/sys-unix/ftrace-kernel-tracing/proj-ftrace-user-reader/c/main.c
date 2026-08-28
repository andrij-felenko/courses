#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>

#define TRACEFS_PATH "/sys/kernel/tracing"
#define BUF_SIZE 4096

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig)
{
    (void)sig;
    g_running = 0;
}

static int write_tracefs(const char *rel_path, const char *val)
{
    char full_path[512];
    snprintf(full_path, sizeof(full_path), "%s/%s", TRACEFS_PATH, rel_path);
    
    int fd = open(full_path, O_WRONLY | O_TRUNC);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", full_path, strerror(errno));
        return -1;
    }
    
    ssize_t len = strlen(val);
    if (write(fd, val, len) != len) {
        fprintf(stderr, "Помилка запису '%s' у %s: %s\n", val, full_path, strerror(errno));
        close(fd);
        return -1;
    }
    
    close(fd);
    return 0;
}

int main(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    printf("[+] Налаштування ftrace через tracefs...\n");

    /* 1. Вимикаємо трасування на час налаштування */
    if (write_tracefs("tracing_on", "0") < 0) return 1;

    /* 2. Очищаємо попередній фільтр */
    if (write_tracefs("set_ftrace_filter", "") < 0) return 1;

    /* 3. Встановлюємо фільтр на функції відкриття файлів */
    if (write_tracefs("set_ftrace_filter", "do_sys_open*") < 0) return 1;

    /* 4. Активуємо плагін function */
    if (write_tracefs("current_tracer", "function") < 0) return 1;

    /* 5. Увімкаємо трасування */
    if (write_tracefs("tracing_on", "1") < 0) return 1;

    printf("[+] ftrace активовано. Зчитування trace_pipe (Ctrl+C для виходу)...\n");

    char pipe_path[512];
    snprintf(pipe_path, sizeof(pipe_path), "%s/trace_pipe", TRACEFS_PATH);
    int pipe_fd = open(pipe_path, O_RDONLY);
    if (pipe_fd < 0) {
        fprintf(stderr, "Помилка відкриття trace_pipe: %s\n", strerror(errno));
        goto cleanup;
    }

    char buffer[BUF_SIZE];
    while (g_running) {
        ssize_t bytes_read = read(pipe_fd, buffer, sizeof(buffer) - 1);
        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            printf("%s", buffer);
            fflush(stdout);
        } else if (bytes_read < 0) {
            if (errno == EINTR) continue;
            fprintf(stderr, "Помилка читання з trace_pipe: %s\n", strerror(errno));
            break;
        }
    }

    close(pipe_fd);

cleanup:
    printf("\n[+] Деактивація ftrace та відновлення стану ядра...\n");
    write_tracefs("tracing_on", "0");
    write_tracefs("current_tracer", "nop");
    write_tracefs("set_ftrace_filter", "");
    printf("[+] Завершено успішно.\n");
    return 0;
}
