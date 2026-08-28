#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <pty.h>
#include <poll.h>
#include <errno.h>

static struct termios g_orig_termios;
static int g_raw_mode_active = 0;

static void restore_terminal_mode(void) {
    if (g_raw_mode_active) {
        tcsetattr(STDIN_FILENO, TCSAFLUSH, &g_orig_termios);
        g_raw_mode_active = 0;
    }
}

static int enable_raw_mode(void) {
    if (tcgetattr(STDIN_FILENO, &g_orig_termios) == -1) {
        return -1;
    }
    struct termios raw = g_orig_termios;
    cfmakeraw(&raw);
    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) {
        return -1;
    }
    g_raw_mode_active = 1;
    atexit(restore_terminal_mode);
    return 0;
}

int main(void) {
    int master_fd = -1;
    struct winsize ws;
    if (ioctl(STDIN_FILENO, TIOCGWINSZ, &ws) == -1) {
        ws.ws_col = 80;
        ws.ws_row = 24;
    }

    pid_t pid = forkpty(&master_fd, NULL, NULL, &ws);
    if (pid < 0) {
        perror("forkpty");
        return 1;
    }

    if (pid == 0) {
        // Дочірній процес: керуючий термінал налаштовано ядром
        char *shell = getenv("SHELL");
        if (!shell) shell = "/bin/sh";
        execlp(shell, shell, "-l", NULL);
        _exit(127);
    }

    // Батьківський процес: переводимо локальний термінал у raw mode
    if (enable_raw_mode() == -1) {
        perror("enable_raw_mode");
        kill(pid, SIGTERM);
        return 1;
    }

    struct pollfd fds[2];
    fds[0].fd = STDIN_FILENO;
    fds[0].events = POLLIN;
    fds[1].fd = master_fd;
    fds[1].events = POLLIN;

    char buffer[4096];
    int running = 1;

    while (running) {
        int ret = poll(fds, 2, -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }

        // Введення від користувача -> запис у майстер PTY
        if (fds[0].revents & POLLIN) {
            ssize_t n = read(STDIN_FILENO, buffer, sizeof(buffer));
            if (n <= 0) break;
            // Перевірка на локальну аварійну послідовність (імітація ~.)
            if (n == 2 && buffer[0] == '~' && buffer[1] == '.') {
                break;
            }
            if (write(master_fd, buffer, (size_t)n) != n) break;
        }

        // Вивід від дочірнього процесу через PTY -> stdout користувача
        if (fds[1].revents & POLLIN) {
            ssize_t n = read(master_fd, buffer, sizeof(buffer));
            if (n <= 0) break;
            if (write(STDOUT_FILENO, buffer, (size_t)n) != n) break;
        }

        if (fds[1].revents & (POLLHUP | POLLERR)) {
            running = 0;
        }
    }

    restore_terminal_mode();
    close(master_fd);
    int status = 0;
    waitpid(pid, &status, 0);
    return WIFEXITED(status) ? WEXITSTATUS(status) : 1;
}
