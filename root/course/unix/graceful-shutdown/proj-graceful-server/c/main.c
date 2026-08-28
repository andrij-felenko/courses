#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <sys/signalfd.h>
#include <sys/timerfd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define MAX_EVENTS 64
#define BUFFER_SIZE 1024
#define SHUTDOWN_TIMEOUT_SEC 5

typedef enum {
    STATE_RUNNING,
    STATE_STOPPING,
    STATE_DRAINING,
    STATE_DONE,
    STATE_TIMEOUT
} server_state_t;

typedef struct {
    int fd;
    char remote_addr[INET_ADDRSTRLEN];
    int remote_port;
} client_conn_t;

static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

static int create_signalfd(void) {
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGINT);

    /* Блокуємо сигнали для всіх потоків процесу */
    if (sigprocmask(SIG_BLOCK, &mask, NULL) == -1) {
        perror("sigprocmask");
        return -1;
    }

    int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd == -1) {
        perror("signalfd");
        return -1;
    }
    return sfd;
}

static int create_timerfd(void) {
    int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
    if (tfd == -1) {
        perror("timerfd_create");
        return -1;
    }
    return tfd;
}

static int arm_timer(int tfd, int seconds) {
    struct itimerspec its;
    memset(&its, 0, sizeof(its));
    its.it_value.tv_sec = seconds;
    its.it_value.tv_nsec = 0;
    return timerfd_settime(tfd, 0, &its, NULL);
}

static int create_listen_socket(int port) {
    int fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (fd == -1) {
        perror("socket");
        return -1;
    }

    int opt = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);

    if (bind(fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
        perror("bind");
        close(fd);
        return -1;
    }

    if (listen(fd, SOMAXCONN) == -1) {
        perror("listen");
        close(fd);
        return -1;
    }
    return fd;
}

int main(int argc, char *argv[]) {
    int port = 8080;
    if (argc > 1) port = atoi(argv[1]);

    printf("[SERVER] Ініціалізація координатора завершення на порту %d...\n", port);

    int epfd = epoll_create1(EPOLL_CLOEXEC);
    if (epfd == -1) {
        perror("epoll_create1");
        return 1;
    }

    int sig_fd = create_signalfd();
    int timer_fd = create_timerfd();
    int listen_fd = create_listen_socket(port);

    if (sig_fd == -1 || timer_fd == -1 || listen_fd == -1) {
        fprintf(stderr, "[SERVER] Критична помилка ініціалізації дескрипторів\n");
        return 1;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = sig_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, sig_fd, &ev);

    ev.events = EPOLLIN;
    ev.data.fd = timer_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, timer_fd, &ev);

    ev.events = EPOLLIN;
    ev.data.fd = listen_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev);

    client_conn_t clients[MAX_EVENTS];
    for (int i = 0; i < MAX_EVENTS; ++i) clients[i].fd = -1;
    int active_clients = 0;

    server_state_t state = STATE_RUNNING;
    struct epoll_event events[MAX_EVENTS];

    printf("[SERVER] Головний цикл запущено (PID: %d). Очікування з'єднань...\n", getpid());

    while (state != STATE_DONE && state != STATE_TIMEOUT) {
        int nfds = epoll_wait(epfd, events, MAX_EVENTS, -1);
        if (nfds == -1) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }

        for (int i = 0; i < nfds; ++i) {
            int cur_fd = events[i].data.fd;

            /* Подія 1: Надходження системного сигналу через signalfd */
            if (cur_fd == sig_fd) {
                struct signalfd_siginfo fdsi;
                ssize_t s = read(sig_fd, &fdsi, sizeof(fdsi));
                if (s == sizeof(fdsi)) {
                    printf("\n[SERVER] Отримано сигнал %d (%s) від PID %d\n",
                           fdsi.ssi_signo,
                           fdsi.ssi_signo == SIGTERM ? "SIGTERM" : "SIGINT",
                           fdsi.ssi_pid);

                    if (state == STATE_RUNNING) {
                        printf("[SERVER] Перехід у режим STOPPING: відсікання нових клієнтів...\n");
                        state = STATE_STOPPING;

                        /* Закриваємо вхідний сокет, щоб не приймати нові з'єднання */
                        epoll_ctl(epfd, EPOLL_CTL_DEL, listen_fd, NULL);
                        close(listen_fd);
                        listen_fd = -1;

                        printf("[SERVER] Запуск таймера дренування на %d секунд...\n", SHUTDOWN_TIMEOUT_SEC);
                        arm_timer(timer_fd, SHUTDOWN_TIMEOUT_SEC);
                        state = STATE_DRAINING;

                        if (active_clients == 0) {
                            printf("[SERVER] Немає активних клієнтів. Завершення миттєве.\n");
                            state = STATE_DONE;
                            break;
                        } else {
                            printf("[SERVER] Очікування завершення %d активних клієнтів...\n", active_clients);
                        }
                    } else if (state == STATE_DRAINING) {
                        printf("[SERVER] Повторний сигнал переривання! Екстрене форсоване завершення.\n");
                        state = STATE_TIMEOUT;
                        break;
                    }
                }
            }
            /* Подія 2: Спрацював сторожовий таймер дедлайну */
            else if (cur_fd == timer_fd) {
                uint64_t expirations;
                read(timer_fd, &expirations, sizeof(expirations));
                printf("[SERVER] ПОМИЛКА: Вичерпано ліміт часу дренування (%d c)!\n", SHUTDOWN_TIMEOUT_SEC);
                printf("[SERVER] Примусове закриття %d завислих клієнтів перед аварійним виходом.\n", active_clients);
                state = STATE_TIMEOUT;
                break;
            }
            /* Подія 3: Новий клієнт під час штатної роботи */
            else if (cur_fd == listen_fd) {
                struct sockaddr_in client_addr;
                socklen_t client_len = sizeof(client_addr);
                int client_fd = accept4(listen_fd, (struct sockaddr*)&client_addr, &client_len,
                                        SOCK_NONBLOCK | SOCK_CLOEXEC);
                if (client_fd != -1) {
                    if (active_clients < MAX_EVENTS) {
                        ev.events = EPOLLIN | EPOLLRDHUP;
                        ev.data.fd = client_fd;
                        epoll_ctl(epfd, EPOLL_CTL_ADD, client_fd, &ev);

                        for (int k = 0; k < MAX_EVENTS; ++k) {
                            if (clients[k].fd == -1) {
                                clients[k].fd = client_fd;
                                inet_ntop(AF_INET, &client_addr.sin_addr, clients[k].remote_addr, sizeof(clients[k].remote_addr));
                                clients[k].remote_port = ntohs(client_addr.sin_port);
                                break;
                            }
                        }
                        active_clients++;
                        printf("[CLIENT] Під'єднано нового клієнта (FD: %d, всього: %d)\n", client_fd, active_clients);
                    } else {
                        /* Переповнення черги з'єднань */
                        close(client_fd);
                    }
                }
            }
            /* Подія 4: Передача даних або закриття з'єднання клієнтом */
            else {
                char buf[BUFFER_SIZE];
                ssize_t bytes_read = read(cur_fd, buf, sizeof(buf) - 1);

                if (bytes_read > 0) {
                    buf[bytes_read] = '\0';
                    /* Ехо-відповідь клієнту */
                    const char *resp_prefix = (state == STATE_DRAINING) ? "HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n" : "OK: ";
                    write(cur_fd, resp_prefix, strlen(resp_prefix));
                    write(cur_fd, buf, bytes_read);

                    if (state == STATE_DRAINING) {
                        /* Під час дренування відправляємо відповідь і закриваємо запис */
                        shutdown(cur_fd, SHUT_WR);
                    }
                } else {
                    /* read == 0 (EOF) або помилка читання */
                    epoll_ctl(epfd, EPOLL_CTL_DEL, cur_fd, NULL);
                    close(cur_fd);

                    for (int k = 0; k < MAX_EVENTS; ++k) {
                        if (clients[k].fd == cur_fd) {
                            clients[k].fd = -1;
                            break;
                        }
                    }
                    active_clients--;
                    printf("[CLIENT] Клієнт від'єднався (FD: %d, лишилося: %d)\n", cur_fd, active_clients);

                    if (state == STATE_DRAINING && active_clients == 0) {
                        printf("[SERVER] Усі клієнтські сесії успішно дреновано.\n");
                        state = STATE_DONE;
                        break;
                    }
                }
            }
        }
    }

    /* Фаза остаточного вивільнення ресурсів */
    printf("[SERVER] Фаза прибирання: звільнення дескрипторів та скидання буферів...\n");
    for (int i = 0; i < MAX_EVENTS; ++i) {
        if (clients[i].fd != -1) {
            close(clients[i].fd);
            clients[i].fd = -1;
        }
    }

    if (listen_fd != -1) close(listen_fd);
    close(sig_fd);
    close(timer_fd);
    close(epfd);
    fflush(stdout);

    if (state == STATE_DONE) {
        printf("[SERVER] Коректне завершення виконано успішно. Код виходу 0.\n");
        return 0;
    } else {
        fprintf(stderr, "[SERVER] Завершення перервано за таймаутом/форсовано. Код виходу 1.\n");
        return 1;
    }
}
