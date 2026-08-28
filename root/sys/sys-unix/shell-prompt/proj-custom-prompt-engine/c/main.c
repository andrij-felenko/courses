#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>

static double get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e6 + (double)ts.tv_nsec * 1e-3;
}

/* Метод 1: Запуск git rev-parse через fork() + execve() */
static int probe_git_fork_exec(char *branch_out, size_t max_len) {
    int pipefd[2];
    if (pipe(pipefd) == -1) return -1;

    pid_t pid = fork();
    if (pid == 0) {
        close(pipefd[0]);
        dup2(pipefd[1], STDOUT_FILENO);
        close(pipefd[1]);
        
        int devnull = open("/dev/null", O_WRONLY);
        if (devnull != -1) {
            dup2(devnull, STDERR_FILENO);
            close(devnull);
        }

        execlp("git", "git", "rev-parse", "--abbrev-ref", "HEAD", NULL);
        _exit(127);
    }

    close(pipefd[1]);
    ssize_t bytes_read = read(pipefd[0], branch_out, max_len - 1);
    close(pipefd[0]);

    int status;
    waitpid(pid, &status, 0);

    if (bytes_read > 0 && WIFEXITED(status) && WEXITSTATUS(status) == 0) {
        branch_out[bytes_read] = '\0';
        char *nl = strchr(branch_out, '\n');
        if (nl) *nl = '\0';
        return 0;
    }
    return -1;
}

/* Метод 2: Пряме читання .git/HEAD без системного fork */
static int probe_git_direct_read(char *branch_out, size_t max_len) {
    int fd = open(".git/HEAD", O_RDONLY);
    if (fd == -1) return -1;

    char buf[256];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);

    if (n <= 0) return -1;
    buf[n] = '\0';

    const char *prefix = "ref: refs/heads/";
    size_t prefix_len = strlen(prefix);
    if (strncmp(buf, prefix, prefix_len) == 0) {
        char *val = buf + prefix_len;
        char *nl = strchr(val, '\n');
        if (nl) *nl = '\0';
        strncpy(branch_out, val, max_len - 1);
        branch_out[max_len - 1] = '\0';
        return 0;
    }
    return -1;
}

int main(void) {
    char branch[128];
    const int iterations = 1000;

    printf("=== Бенчмарк отримання Git-статусу (%d ітерацій) ===\n", iterations);

    /* Тест fork() + execve() */
    double start = get_time_us();
    for (int i = 0; i < iterations; ++i) {
        probe_git_fork_exec(branch, sizeof(branch));
    }
    double elapsed_fork = (get_time_us() - start) / iterations;
    printf("1. fork() + execve(\"git\"): %.2f мкс / виклик (%.3f мс)\n", 
           elapsed_fork, elapsed_fork / 1000.0);

    /* Тест прямого читання файлу */
    start = get_time_us();
    for (int i = 0; i < iterations; ++i) {
        probe_git_direct_read(branch, sizeof(branch));
    }
    double elapsed_direct = (get_time_us() - start) / iterations;
    printf("2. Пряме читання .git/HEAD:  %.2f мкс / виклик (%.3f мс)\n", 
           elapsed_direct, elapsed_direct / 1000.0);

    printf("Прискорення: %.1fx без створення нових процесів.\n", 
           elapsed_fork / elapsed_direct);

    return 0;
}
