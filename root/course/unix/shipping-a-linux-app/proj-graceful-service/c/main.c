#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <sys/signalfd.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdbool.h>

#define MAX_EVENTS 64
#define BUFFER_SIZE 4096
#define DEFAULT_PORT 8080
#define SD_LISTEN_FDS_START 3

/* Автономне надсилання сповіщення стану в systemd через NOTIFY_SOCKET */
static void notify_systemd(const char *state) {
    const char *sock_path = getenv("NOTIFY_SOCKET");
    if (!sock_path || !state) return;

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;

    size_t len = strlen(sock_path);
    if (len >= sizeof(addr.sun_path)) return;

    if (sock_path[0] == '@') {
        addr.sun_path[0] = '\0';
        memcpy(&addr.sun_path[1], &sock_path[1], len - 1);
    } else {
        memcpy(addr.sun_path, sock_path, len);
    }

    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return;

    socklen_t addr_len = offsetof(struct sockaddr_un, sun_path) + len;
    sendto(fd, state, strlen(state), MSG_NOSIGNAL, (struct sockaddr *)&addr, addr_len);
    close(fd);
}

/* Переведення дескриптора у неблокуючий режим введення-виведення */
static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

/* Отримання сокета: підтримка socket activation від systemd або створення власного */
static int get_listen_socket(int port) {
    const char *listen_pid_str = getenv("LISTEN_PID");
    const char *listen_fds_str = getenv("LISTEN_FDS");

    if (listen_pid_str && listen_fds_str) {
        pid_t listen_pid = (pid_t)atoi(listen_pid_str);
        int listen_fds = atoi(listen_fds_str);
        if (listen_pid == getpid() && listen_fds > 0) {
            fprintf(stdout, "<6>Успішно підключено сокет від systemd (fd=%d)\n", SD_LISTEN_FDS_START);
            set_nonblocking(SD_LISTEN_FDS_START);
            return SD_LISTEN_FDS_START;
        }
    }

    int fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    int opt = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons((uint16_t)port);

    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(fd);
        return -1;
    }

    if (listen(fd, SOMAXCONN) < 0) {
        perror("listen");
        close(fd);
        return -1;
    }

    fprintf(stdout, "<6>Створено локальний сокет на порту %d\n", port);
    return fd;
}

int main(int argc, char *argv[]) {
    int port = DEFAULT_PORT;
    if (argc > 1) {
        port = atoi(argv[1]);
    }

    /* 1. Ігноруємо SIGPIPE, щоб уникнути падіння процесу при раптовому закритті клієнтом */
    signal(SIGPIPE, SIG_IGN);

    /* 2. Блокуємо сигнали для безпечної обробки через signalfd */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGHUP);

    if (sigprocmask(SIG_BLOCK, &mask, NULL) < 0) {
        perror("sigprocmask");
        return EXIT_FAILURE;
    }

    int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd < 0) {
        perror("signalfd");
        return EXIT_FAILURE;
    }

    /* 3. Створюємо інстанс epoll */
    int epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (epoll_fd < 0) {
        perror("epoll_create1");
        close(sfd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = sfd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, sfd, &ev);

    /* 4. Отримуємо мережевий сокет */
    int listen_fd = get_listen_socket(port);
    if (listen_fd < 0) {
        close(sfd);
        close(epoll_fd);
        return EXIT_FAILURE;
    }

    ev.events = EPOLLIN;
    ev.data.fd = listen_fd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listen_fd, &ev);

    /* 5. Сповіщаємо systemd про успішну готовність */
    notify_systemd("READY=1\nSTATUS=Сервер успішно готовий приймати трафік");

    struct epoll_event events[MAX_EVENTS];
    bool running = true;
    int active_connections = 0;

    fprintf(stdout, "<6>Головний цикл введення-виведення запущено\n");

    while (running || active_connections > 0) {
        int timeout = running ? 5000 : 1000;
        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, timeout);

        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }

        if (nfds == 0 && running) {
            /* Відправляємо keep-alive сигнал сторожовому таймеру */
            notify_systemd("WATCHDOG=1");
            continue;
        }

        for (int i = 0; i < nfds; i++) {
            int cur_fd = events[i].data.fd;

            if (cur_fd == sfd) {
                /* Обробка системного сигналу як події введення-виведення */
                struct signalfd_siginfo fdsi;
                ssize_t s = read(sfd, &fdsi, sizeof(fdsi));
                if (s == sizeof(fdsi)) {
                    if (fdsi.ssi_signo == SIGTERM || fdsi.ssi_signo == SIGINT) {
                        fprintf(stdout, "<5>Отримано сигнал %d: початок Graceful Shutdown...\n", fdsi.ssi_signo);
                        notify_systemd("STOPPING=1\nSTATUS=Зупинка: дообробка активних з'єднань");
                        running = false;
                        /* Закриваємо сокет прослуховування, щоб відхиляти нових клієнтів */
                        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, listen_fd, NULL);
                        close(listen_fd);
                    } else if (fdsi.ssi_signo == SIGHUP) {
                        fprintf(stdout, "<6>Отримано SIGHUP: перезавантаження конфігурації\n");
                        notify_systemd("RELOADING=1");
                        /* Перечитування файлів конфігурації */
                        notify_systemd("READY=1\nSTATUS=Конфігурацію успішно оновлено");
                    }
                }
            } else if (cur_fd == listen_fd) {
                /* Прийом нових вхідних TCP-з'єднань */
                while (true) {
                    struct sockaddr_in client_addr;
                    socklen_t client_len = sizeof(client_addr);
                    int client_fd = accept4(listen_fd, (struct sockaddr *)&client_addr,
                                            &client_len, SOCK_NONBLOCK | SOCK_CLOEXEC);
                    if (client_fd < 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                        perror("accept4");
                        break;
                    }

                    ev.events = EPOLLIN | EPOLLRDHUP;
                    ev.data.fd = client_fd;
                    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &ev);
                    active_connections++;
                }
            } else {
                /* Обробка даних від клієнтських сокетів */
                char buffer[BUFFER_SIZE];
                ssize_t count = read(cur_fd, buffer, sizeof(buffer));

                if (count > 0) {
                    /* Ехо-відповідь клієнту з прапорцем безпеки MSG_NOSIGNAL */
                    send(cur_fd, buffer, (size_t)count, MSG_NOSIGNAL);
                } else if (count == 0 || (count < 0 && errno != EAGAIN)) {
                    /* Клієнт закрив сокет або сталася помилка передачі */
                    epoll_ctl(epoll_fd, EPOLL_CTL_DEL, cur_fd, NULL);
                    close(cur_fd);
                    active_connections--;
                }
            }
        }
    }

    fprintf(stdout, "<6>Усі клієнтські сесії завершено. Процес виходить штатно.\n");
    close(sfd);
    close(epoll_fd);
    return EXIT_SUCCESS;
}
