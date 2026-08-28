#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <pty.h>
#include <termios.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <poll.h>

#define SOCKET_PATH "/tmp/miniplex.sock"
#define DETACH_KEY 0x1d /* Ctrl+] */
#define BUFFER_SIZE 4096

static struct termios orig_termios;
static int raw_mode_active = 0;

static void restore_terminal(void) {
    if (raw_mode_active) {
        tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios);
        raw_mode_active = 0;
    }
}

static int enable_raw_mode(void) {
    if (tcgetattr(STDIN_FILENO, &orig_termios) < 0) {
        return -1;
    }
    struct termios raw = orig_termios;
    raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
    raw.c_oflag &= ~(OPOST);
    raw.c_cflag |= (CS8);
    raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
    raw.c_cc[VMIN] = 1;
    raw.c_cc[VTIME] = 0;
    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) < 0) {
        return -1;
    }
    raw_mode_active = 1;
    atexit(restore_terminal);
    return 0;
}

static int forward_data(int src_fd, int dst_fd, int check_detach) {
    char buf[BUFFER_SIZE];
    ssize_t n = read(src_fd, buf, sizeof(buf));
    if (n <= 0) {
        return -1;
    }
    if (check_detach) {
        for (ssize_t i = 0; i < n; ++i) {
            if ((unsigned char)buf[i] == DETACH_KEY) {
                return 1; /* Сигнал від'єднання */
            }
        }
    }
    ssize_t written = 0;
    while (written < n) {
        ssize_t res = write(dst_fd, buf + written, (size_t)(n - written));
        if (res < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        written += res;
    }
    return 0;
}

static void run_server(void) {
    int master_fd;
    pid_t pid = forkpty(&master_fd, NULL, NULL, NULL);
    if (pid < 0) {
        perror("forkpty");
        exit(EXIT_FAILURE);
    }
    if (pid == 0) {
        execl("/bin/sh", "sh", NULL);
        _exit(EXIT_FAILURE);
    }

    unlink(SOCKET_PATH);
    int listen_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);

    if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        exit(EXIT_FAILURE);
    }
    if (listen(listen_fd, 1) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    /* Фоновий цикл сервера */
    while (1) {
        int client_fd = accept(listen_fd, NULL, NULL);
        if (client_fd < 0) {
            if (errno == EINTR) continue;
            break;
        }

        struct pollfd fds[2];
        fds[0].fd = master_fd;
        fds[0].events = POLLIN;
        fds[1].fd = client_fd;
        fds[1].events = POLLIN;

        int active = 1;
        while (active) {
            int ret = poll(fds, 2, -1);
            if (ret < 0) {
                if (errno == EINTR) continue;
                break;
            }

            if (fds[0].revents & (POLLIN | POLLERR | POLLHUP)) {
                if (forward_data(master_fd, client_fd, 0) < 0) {
                    /* Дочірній процес завершився */
                    close(client_fd);
                    close(master_fd);
                    close(listen_fd);
                    unlink(SOCKET_PATH);
                    waitpid(pid, NULL, 0);
                    return;
                }
            }

            if (fds[1].revents & (POLLIN | POLLERR | POLLHUP)) {
                int status = forward_data(client_fd, master_fd, 0);
                if (status < 0) {
                    /* Клієнт від'єднався */
                    active = 0;
                }
            }
        }
        close(client_fd);
    }
    close(master_fd);
    close(listen_fd);
    unlink(SOCKET_PATH);
}

static void run_client(void) {
    int sock_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sock_fd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);

    if (connect(sock_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("connect to /tmp/miniplex.sock");
        close(sock_fd);
        exit(EXIT_FAILURE);
    }

    if (enable_raw_mode() < 0) {
        perror("enable_raw_mode");
        close(sock_fd);
        exit(EXIT_FAILURE);
    }

    struct pollfd fds[2];
    fds[0].fd = STDIN_FILENO;
    fds[0].events = POLLIN;
    fds[1].fd = sock_fd;
    fds[1].events = POLLIN;

    while (1) {
        int ret = poll(fds, 2, -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }

        if (fds[0].revents & POLLIN) {
            int status = forward_data(STDIN_FILENO, sock_fd, 1);
            if (status == 1) {
                /* Натиснуто комбінацію від'єднання Ctrl+] */
                break;
            }
            if (status < 0) break;
        }

        if (fds[1].revents & (POLLIN | POLLERR | POLLHUP)) {
            if (forward_data(sock_fd, STDOUT_FILENO, 0) < 0) {
                break;
            }
        }
    }

    restore_terminal();
    close(sock_fd);
}

int main(int argc, char *argv[]) {
    if (argc > 1 && strcmp(argv[1], "--server") == 0) {
        run_server();
    } else if (argc > 1 && strcmp(argv[1], "--client") == 0) {
        run_client();
    } else {
        fprintf(stderr, "Ужиток: %s --server | --client\n", argv[0]);
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
