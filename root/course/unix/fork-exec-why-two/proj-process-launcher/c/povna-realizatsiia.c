#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <signal.h>
#include <sys/syscall.h>

typedef struct {
    const char *executable;
    char *const *argv;
    char *const *envp;
    const char *working_dir;
    int stdin_fd;
    int stdout_fd;
    int stderr_fd;
    rlim_t max_memory_bytes;
    rlim_t max_cpu_seconds;
} ProcessConfig;

/* Допоміжне закриття дескрипторів вище збережених */
static void close_inherited_fds(int min_fd) {
#if defined(__NR_close_range)
    if (syscall(__NR_close_range, min_fd, ~0U, 0) == 0) {
        return;
    }
#endif
    long max_fd = sysconf(_SC_OPEN_MAX);
    if (max_fd < 0 || max_fd > 4096) max_fd = 4096;
    for (int fd = min_fd; fd < max_fd; ++fd) {
        close(fd);
    }
}

int launch_process(const ProcessConfig *cfg, pid_t *out_pid) {
    if (!cfg || !cfg->executable || !cfg->argv) {
        errno = EINVAL;
        return -1;
    }

    int err_pipe[2];
    if (pipe2(err_pipe, O_CLOEXEC) == -1) {
        return -1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        int saved_errno = errno;
        close(err_pipe[0]);
        close(err_pipe[1]);
        errno = saved_errno;
        return -1;
    }

    if (pid == 0) {
        /* ДОЧІРНІЙ ПРОЦЕС: ВІКНО НАЛАШТУВАННЯ */
        close(err_pipe[0]); /* Читаючий кінець дитині не потрібен */

        /* 1. Ізоляція групи процесів */
        if (setpgid(0, 0) == -1) goto child_failure;

        /* 2. Зміна робочого каталогу */
        if (cfg->working_dir && chdir(cfg->working_dir) == -1) {
            goto child_failure;
        }

        /* 3. Встановлення ліміту пам'яті (RLIMIT_AS) */
        if (cfg->max_memory_bytes > 0) {
            struct rlimit mem_lim = {
                .rlim_cur = cfg->max_memory_bytes,
                .rlim_max = cfg->max_memory_bytes
            };
            if (setrlimit(RLIMIT_AS, &mem_lim) == -1) goto child_failure;
        }

        /* 4. Встановлення ліміту часу процесора (RLIMIT_CPU) */
        if (cfg->max_cpu_seconds > 0) {
            struct rlimit cpu_lim = {
                .rlim_cur = cfg->max_cpu_seconds,
                .rlim_max = cfg->max_cpu_seconds
            };
            if (setrlimit(RLIMIT_CPU, &cpu_lim) == -1) goto child_failure;
        }

        /* 5. Перенаправлення дескрипторів STDIN, STDOUT, STDERR */
        if (cfg->stdin_fd >= 0 && cfg->stdin_fd != STDIN_FILENO) {
            if (dup2(cfg->stdin_fd, STDIN_FILENO) == -1) goto child_failure;
        }
        if (cfg->stdout_fd >= 0 && cfg->stdout_fd != STDOUT_FILENO) {
            if (dup2(cfg->stdout_fd, STDOUT_FILENO) == -1) goto child_failure;
        }
        if (cfg->stderr_fd >= 0 && cfg->stderr_fd != STDERR_FILENO) {
            if (dup2(cfg->stderr_fd, STDERR_FILENO) == -1) goto child_failure;
        }

        /* 6. Скидання маски блокування сигналів */
        sigset_t empty_mask;
        sigemptyset(&empty_mask);
        if (sigprocmask(SIG_SETMASK, &empty_mask, NULL) == -1) goto child_failure;

        /* 7. Закриття всіх сторонніх дескрипторів, крім діагностичного каналу */
        close_inherited_fds(3);

        /* 8. Заміна образу пам'яті */
        if (cfg->envp) {
            execvpe(cfg->executable, cfg->argv, cfg->envp);
        } else {
            execvp(cfg->executable, cfg->argv);
        }

child_failure:
        {
            int child_errno = errno;
            /* Записуємо код помилки в діагностичний канал */
            ssize_t written = write(err_pipe[1], &child_errno, sizeof(child_errno));
            (void)written;
            close(err_pipe[1]);
            _exit(127);
        }
    }

    /* БАТЬКІВСЬКИЙ ПРОЦЕС */
    close(err_pipe[1]); /* Закриваємо записуючий кінець у батьку */

    int child_error = 0;
    ssize_t bytes_read;
    
    /* Читання з обробкою переривання сигналами EINTR */
    do {
        bytes_read = read(err_pipe[0], &child_error, sizeof(child_error));
    } while (bytes_read == -1 && errno == EINTR);

    close(err_pipe[0]);

    if (bytes_read == sizeof(child_error)) {
        /* Дочірній процес повідомив про помилку перед виходом */
        waitpid(pid, NULL, 0); /* Прибираємо зомбі */
        errno = child_error;
        return -1;
    }

    if (bytes_read == 0) {
        /* Канал закрився автоматично ядром через O_CLOEXEC: запуск успішний */
        if (out_pid) *out_pid = pid;
        return 0;
    }

    /* Неочікуваний збій читання каналу */
    waitpid(pid, NULL, 0);
    return -1;
}
