#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

static volatile sig_atomic_t g_running = 1;
static volatile sig_atomic_t g_child_dead = 0;

static void handle_sigterm(int sig) {
    (void)sig;
    g_running = 0;
}

static void handle_sigchld(int sig) {
    (void)sig;
    g_child_dead = 1;
}

/* Неблокуюча перевірка доступності локального TCP-порту */
static int probe_local_port(int port, int timeout_ms) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        return -1;
    }

    int flags = fcntl(fd, F_GETFL, 0);
    if (flags < 0 || fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        close(fd);
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons((uint16_t)port);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    int res = connect(fd, (struct sockaddr*)&addr, sizeof(addr));
    if (res == 0) {
        close(fd);
        return 0; /* Порт негайно відповів */
    }

    if (errno != EINPROGRESS) {
        close(fd);
        return -1; /* Порт закритий або збій */
    }

    struct pollfd pfd;
    pfd.fd = fd;
    pfd.events = POLLOUT;
    pfd.revents = 0;

    int poll_res = poll(&pfd, 1, timeout_ms);
    if (poll_res > 0 && (pfd.revents & POLLOUT)) {
        int err = 0;
        socklen_t len = sizeof(err);
        if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &err, &len) == 0 && err == 0) {
            close(fd);
            return 0; /* Успішне підключення */
        }
    }

    close(fd);
    return -1;
}

/* Запуск процесу SSH у фоновому режимі */
static pid_t launch_ssh_tunnel(const char *host, int local_port, const char *remote_dest) {
    char forward_arg[256];
    snprintf(forward_arg, sizeof(forward_arg), "%d:%s", local_port, remote_dest);

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return -1;
    }

    if (pid == 0) {
        /* Дочірній процес: запуск клієнта OpenSSH */
        char *args[] = {
            "ssh",
            "-N",
            "-L", forward_arg,
            "-o", "ExitOnForwardFailure=yes",
            "-o", "ServerAliveInterval=15",
            "-o", "ServerAliveCountMax=3",
            "-o", "BatchMode=yes",
            (char *)host,
            NULL
        };
        execvp("ssh", args);
        perror("execvp ssh");
        _exit(127);
    }

    return pid;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <ssh_host> <local_port> <remote_host:port>\n", argv[0]);
        fprintf(stderr, "Приклад: %s user@gateway.domain 5432 10.0.1.5:5432\n", argv[0]);
        return 1;
    }

    const char *ssh_host = argv[1];
    int local_port = atoi(argv[2]);
    const char *remote_dest = argv[3];

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_sigterm;
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT, &sa, NULL);

    struct sigaction sc;
    memset(&sc, 0, sizeof(sc));
    sc.sa_handler = handle_sigchld;
    sc.sa_flags = SA_RESTART | SA_NOCLDSTOP;
    sigaction(SIGCHLD, &sc, NULL);

    signal(SIGPIPE, SIG_IGN);

    printf("[supervisor] Запуск супервізора тунелю для 127.0.0.1:%d -> %s через %s\n",
           local_port, remote_dest, ssh_host);

    pid_t child_pid = -1;
    int backoff_sec = 2;

    while (g_running) {
        if (child_pid <= 0) {
            printf("[supervisor] Запуск процесу ssh...\n");
            child_pid = launch_ssh_tunnel(ssh_host, local_port, remote_dest);
            if (child_pid <= 0) {
                sleep((unsigned int)backoff_sec);
                backoff_sec = (backoff_sec < 30) ? backoff_sec * 2 : 30;
                continue;
            }
            g_child_dead = 0;
            sleep(2); /* Пауза на ініціалізацію сокета */
        }

        if (g_child_dead) {
            int status;
            pid_t p = waitpid(child_pid, &status, WNOHANG);
            if (p > 0) {
                printf("[supervisor] Процес ssh (PID %d) завершився зі статусом %d\n", child_pid, status);
                child_pid = -1;
                sleep((unsigned int)backoff_sec);
                continue;
            }
        }

        /* Зондуємо локальний порт */
        if (probe_local_port(local_port, 1000) == 0) {
            backoff_sec = 2; /* Тунель здоровий, скидаємо затримку */
            sleep(5);
        } else {
            printf("[supervisor] Зонд не вдався! Локальний порт %d не відповідає.\n", local_port);
            if (child_pid > 0) {
                kill(child_pid, SIGTERM);
                sleep(1);
                kill(child_pid, SIGKILL);
                waitpid(child_pid, NULL, 0);
                child_pid = -1;
            }
            sleep((unsigned int)backoff_sec);
            backoff_sec = (backoff_sec < 30) ? backoff_sec * 2 : 30;
        }
    }

    if (child_pid > 0) {
        printf("[supervisor] Зупинка дочірнього процесу ssh (PID %d)...\n", child_pid);
        kill(child_pid, SIGTERM);
        waitpid(child_pid, NULL, 0);
    }

    printf("[supervisor] Роботу завершено.\n");
    return 0;
}
