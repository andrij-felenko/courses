#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <poll.h>

static int g_client_fd = -1;

// Сигнальний обробник SIGURG
static void handle_sigurg(int sig) {
    (void)sig;
    char oob_byte;
    int saved_errno = errno;

    // Читаємо терміновий байт із прапорцем MSG_OOB
    ssize_t n = recv(g_client_fd, &oob_byte, 1, MSG_OOB);
    if (n > 0) {
        // Використовуємо async-signal-safe системний виклик write
        const char msg[] = "\n[SIGURG Handler] OOB byte received: ";
        write(STDOUT_FILENO, msg, sizeof(msg) - 1);
        write(STDOUT_FILENO, &oob_byte, 1);
        write(STDOUT_FILENO, "\n", 1);
    } else if (n < 0) {
        if (errno == EWOULDBLOCK || errno == EAGAIN) {
            // Байт ще в дорозі або вже прочитаний
        }
    }

    errno = saved_errno;
}

int main(void) {
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket");
        return 1;
    }

    int reuse = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(9099);

    if (bind(listen_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(listen_fd);
        return 1;
    }

    if (listen(listen_fd, 5) < 0) {
        perror("listen");
        close(listen_fd);
        return 1;
    }

    printf("Server listening on port 9099...\n");
    g_client_fd = accept(listen_fd, NULL, NULL);
    if (g_client_fd < 0) {
        perror("accept");
        close(listen_fd);
        return 1;
    }
    printf("Client connected, fd=%d\n", g_client_fd);

    // Налаштовуємо сигнальний обробник SIGURG
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_sigurg;
    sa.sa_flags = SA_RESTART;
    sigaction(SIGURG, &sa, NULL);

    // Призначаємо поточний процес власником сокета
    if (fcntl(g_client_fd, F_SETOWN, getpid()) < 0) {
        perror("fcntl F_SETOWN");
    }

    // Головний цикл з poll()
    struct pollfd fds[1];
    fds[0].fd = g_client_fd;
    fds[0].events = POLLIN | POLLPRI;

    char buf[128];
    while (1) {
        int ret = poll(fds, 1, -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            perror("poll");
            break;
        }

        // Перевіряємо наявність виняткового стану (OOB data)
        if (fds[0].revents & POLLPRI) {
            printf("[poll] POLLPRI event detected!\n");
            char oob_c;
            ssize_t res = recv(g_client_fd, &oob_c, 1, MSG_OOB);
            if (res > 0) {
                printf("[poll] OOB Byte read via MSG_OOB: '%c'\n", oob_c);
            }
        }

        // Перевіряємо наявність звичайних даних для читання
        if (fds[0].revents & POLLIN) {
            int atmark = 0;
            ioctl(g_client_fd, SIOCATMARK, &atmark);
            if (atmark) {
                printf("[poll] Socket is currently at OOB mark!\n");
            }

            ssize_t n = recv(g_client_fd, buf, sizeof(buf) - 1, 0);
            if (n <= 0) {
                if (n == 0) printf("Client disconnected.\n");
                else perror("recv");
                break;
            }
            buf[n] = '\0';
            printf("Received normal data (%zd bytes): %s", n, buf);
        }
    }

    close(g_client_fd);
    close(listen_fd);
    return 0;
}
