#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include <string.h>
#include <errno.h>
#include <time.h>

static volatile sig_atomic_t g_running = 1;
static volatile sig_atomic_t g_reload_requested = 0;

static void handle_sigterm(int signum) {
    (void)signum;
    g_running = 0;
}

static void handle_sighup(int signum) {
    (void)signum;
    g_reload_requested = 1;
}

int daemonize_process(const char *work_dir, const char *log_path) {
    /* 1. Скидання маски створення файлів */
    umask(0);

    /* 2. Перший fork: відокремлення від оболонки */
    pid_t pid = fork();
    if (pid < 0) {
        return -1;
    }
    if (pid > 0) {
        _exit(0); /* Завершуємо оригінального батька */
    }

    /* 3. Створення нового сеансу (втрата controlling TTY) */
    if (setsid() < 0) {
        return -1;
    }

    /* 4. Другий fork: позбавлення статусу лідера сесії */
    pid = fork();
    if (pid < 0) {
        return -1;
    }
    if (pid > 0) {
        _exit(0); /* Завершуємо першого нащадка (лідера сесії) */
    }

    /* 5. Зміна робочого каталогу на безпечний */
    if (chdir(work_dir ? work_dir : "/") < 0) {
        return -1;
    }

    /* 6. Налаштування обробників сигналів */
    struct sigaction sa_term;
    memset(&sa_term, 0, sizeof(sa_term));
    sa_term.sa_handler = handle_sigterm;
    sigemptyset(&sa_term.sa_mask);
    sigaction(SIGTERM, &sa_term, NULL);

    struct sigaction sa_hup;
    memset(&sa_hup, 0, sizeof(sa_hup));
    sa_hup.sa_handler = handle_sighup;
    sigemptyset(&sa_hup.sa_mask);
    sigaction(SIGHUP, &sa_hup, NULL);

    /* 7. Ізоляція стандартних файлових дескрипторів */
    int null_fd = open("/dev/null", O_RDWR);
    if (null_fd < 0) {
        return -1;
    }

    int log_fd = null_fd;
    if (log_path != NULL) {
        log_fd = open(log_path, O_WRONLY | O_CREAT | O_APPEND, 0644);
        if (log_fd < 0) {
            log_fd = null_fd;
        }
    }

    /* stdin -> /dev/null */
    dup2(null_fd, STDIN_FILENO);
    /* stdout -> log_file або /dev/null */
    dup2(log_fd, STDOUT_FILENO);
    /* stderr -> log_file або /dev/null */
    dup2(log_fd, STDERR_FILENO);

    if (null_fd > 2) {
        close(null_fd);
    }
    if (log_fd > 2 && log_fd != null_fd) {
        close(log_fd);
    }

    return 0;
}

int main(void) {
    if (daemonize_process("/", "/tmp/daemon_worker.log") < 0) {
        perror("daemonize failed");
        return 1;
    }

    printf("Daemon started successfully with PID %d\n", getpid());
    fflush(stdout);

    while (g_running) {
        if (g_reload_requested) {
            g_reload_requested = 0;
            printf("SIGHUP received: reloading configuration at %ld\n", (long)time(NULL));
            fflush(stdout);
        }
        sleep(2);
    }

    printf("SIGTERM received: shutting down gracefully\n");
    fflush(stdout);
    return 0;
}
