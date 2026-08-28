/* Безпечна передача секрету нащадку через анонімний пайп мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <sys/wait.h>

#define SECRET_FD 3

void run_child_secure(int read_fd) {
    /* Перенаправляємо read_fd на фіксований SECRET_FD (3) */
    if (read_fd != SECRET_FD) {
        if (dup2(read_fd, SECRET_FD) < 0) {
            perror("dup2");
            exit(EXIT_FAILURE);
        }
        close(read_fd);
    }

    /* Знімаємо O_CLOEXEC з SECRET_FD, щоб він зберігся після execve */
    int flags = fcntl(SECRET_FD, F_GETFD);
    fcntl(SECRET_FD, F_SETFD, flags & ~FD_CLOEXEC);

    /* Очищене середовище: жодних паролів у envp */
    char *const clean_env[] = {
        "PATH=/usr/bin:/bin",
        "LANG=C.UTF-8",
        NULL
    };

    char *const child_args[] = {
        "/usr/local/bin/worker",
        "--secret-fd=3",
        NULL
    };

    execve(child_args[0], child_args, clean_env);
    perror("execve");
    exit(EXIT_FAILURE);
}

int main(void) {
    int fds[2];
    if (pipe2(fds, O_CLOEXEC) < 0) {
        perror("pipe2");
        return EXIT_FAILURE;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        /* Дочірній процес: закриваємо записуючий кінець */
        close(fds[1]);
        run_child_secure(fds[0]);
    } else {
        /* Батьківський процес: закриваємо читаючий кінець */
        close(fds[0]);

        const char secret_data[] = "SuperSecret_Database_Token_2026";
        ssize_t written = write(fds[1], secret_data, sizeof(secret_data));
        (void)written;

        /* Закриття fds[1] надсилає EOF дочірньому процесу */
        close(fds[1]);

        waitpid(pid, NULL, 0);
    }
    return EXIT_SUCCESS;
}
