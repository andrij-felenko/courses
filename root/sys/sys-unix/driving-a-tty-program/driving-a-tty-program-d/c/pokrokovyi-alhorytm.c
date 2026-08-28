#define _XOPEN_SOURCE 600
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

pid_t spawn_under_pty(const char *file, char *const argv[], int *out_master_fd) {
    int master_fd = posix_openpt(O_RDWR | O_NOCTTY);
    if (master_fd < 0) {
        perror("posix_openpt");
        return -1;
    }

    if (grantpt(master_fd) < 0 || unlockpt(master_fd) < 0) {
        perror("grantpt/unlockpt");
        close(master_fd);
        return -1;
    }

    char *slave_name = ptsname(master_fd);
    if (!slave_name) {
        perror("ptsname");
        close(master_fd);
        return -1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        close(master_fd);
        return -1;
    }

    if (pid == 0) {
        /* Дочірній процес */
        close(master_fd);

        /* Створюємо новий сеанс без успадкованого TTY */
        if (setsid() < 0) {
            perror("setsid");
            _exit(1);
        }

        /* Відкриваємо підлеглий кінець */
        int slave_fd = open(slave_name, O_RDWR);
        if (slave_fd < 0) {
            perror("open slave");
            _exit(1);
        }

        /* Призначаємо PTY керівним терміналом сеансу */
        if (ioctl(slave_fd, TIOCSCTTY, 0) < 0) {
            perror("ioctl TIOCSCTTY");
            _exit(1);
        }

        /* Перенаправляємо stdin, stdout, stderr */
        dup2(slave_fd, STDIN_FILENO);
        dup2(slave_fd, STDOUT_FILENO);
        dup2(slave_fd, STDERR_FILENO);

        if (slave_fd > STDERR_FILENO) {
            close(slave_fd);
        }

        execvp(file, argv);
        perror("execvp");
        _exit(127);
    }

    /* Батьківський процес */
    *out_master_fd = master_fd;
    return pid;
}
