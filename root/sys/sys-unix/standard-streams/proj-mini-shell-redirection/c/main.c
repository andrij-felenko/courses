#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <errno.h>

// Виконання однієї команди з перенаправленням stdout у файл
int run_with_stdout_redirect(const char *cmd, char *const argv[], const char *filepath) {
    // 1. Очищаємо всі користувацькі буфери stdio перед розгалуженням!
    if (fflush(NULL) != 0) {
        perror("fflush failed");
        return -1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed");
        return -1;
    }

    if (pid == 0) {
        // Дочірній процес: відкриваємо файл для запису
        int fd = open(filepath, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd < 0) {
            perror("open output file failed");
            _exit(1);
        }

        // Атомарно перенаправляємо STDOUT_FILENO (1) на відкритий файл
        if (dup2(fd, STDOUT_FILENO) < 0) {
            perror("dup2 failed");
            close(fd);
            _exit(1);
        }

        // Закриваємо оригінальний дескриптор, оскільки 1 тепер вказує на цей файл
        close(fd);

        // Замінюємо образ процесу цільовою програмою
        execvp(cmd, argv);
        
        // Сюди код потрапляє лише у разі помилки execvp
        perror("execvp failed");
        _exit(127);
    }

    // Батьківський процес чекає на завершення дочірнього з обробкою EINTR
    int status = 0;
    while (waitpid(pid, &status, 0) < 0) {
        if (errno != EINTR) {
            return -1;
        }
    }

    return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
}

// Виконання двокомпонентного конвеєра: cmd1_argv | cmd2_argv
int run_pipeline(char *const cmd1_argv[], char *const cmd2_argv[]) {
    // Очищаємо буфери перед створенням процесів
    fflush(NULL);

    int pipefd[2];
    if (pipe(pipefd) < 0) {
        perror("pipe creation failed");
        return -1;
    }

    // Створюємо перший дочірній процес (Письменник)
    pid_t pid1 = fork();
    if (pid1 < 0) {
        perror("fork pid1 failed");
        close(pipefd[0]);
        close(pipefd[1]);
        return -1;
    }

    if (pid1 == 0) {
        // Дочірній процес 1: читальний кінець йому не потрібен
        close(pipefd[0]);

        // Перенаправляємо stdout у писальний кінець каналу (pipefd[1])
        if (dup2(pipefd[1], STDOUT_FILENO) < 0) {
            perror("dup2 pid1 failed");
            _exit(1);
        }
        close(pipefd[1]);

        execvp(cmd1_argv[0], cmd1_argv);
        perror("execvp cmd1 failed");
        _exit(127);
    }

    // Створюємо другий дочірній процес (Читач)
    pid_t pid2 = fork();
    if (pid2 < 0) {
        perror("fork pid2 failed");
        close(pipefd[0]);
        close(pipefd[1]);
        return -1;
    }

    if (pid2 == 0) {
        // Дочірній процес 2: писальний кінець йому не потрібен
        close(pipefd[1]);

        // Перенаправляємо stdin на читальний кінець каналу (pipefd[0])
        if (dup2(pipefd[0], STDIN_FILENO) < 0) {
            perror("dup2 pid2 failed");
            _exit(1);
        }
        close(pipefd[0]);

        execvp(cmd2_argv[0], cmd2_argv);
        perror("execvp cmd2 failed");
        _exit(127);
    }

    // Критичний момент: батьківський процес ПОВИНЕН закрити обидва кінці каналу!
    close(pipefd[0]);
    close(pipefd[1]);

    // Очікуємо на завершення обох дочірніх процесів
    int status1 = 0, status2 = 0;
    while (waitpid(pid1, &status1, 0) < 0) {
        if (errno != EINTR) break;
    }
    while (waitpid(pid2, &status2, 0) < 0) {
        if (errno != EINTR) break;
    }

    return WIFEXITED(status2) ? WEXITSTATUS(status2) : -1;
}

int main(void) {
    printf("[C] Тестування перенаправлення stdout у файл result.txt...\n");
    char *args_ls[] = {"ls", "-l", "/", NULL};
    if (run_with_stdout_redirect("ls", args_ls, "result.txt") == 0) {
        printf("[C] Успішно збережено виведення ls у result.txt\n");
    }

    printf("[C] Тестування конвеєра: ls -la / | grep etc...\n");
    char *cmd1[] = {"ls", "-la", "/", NULL};
    char *cmd2[] = {"grep", "etc", NULL};
    run_pipeline(cmd1, cmd2);

    return 0;
}
