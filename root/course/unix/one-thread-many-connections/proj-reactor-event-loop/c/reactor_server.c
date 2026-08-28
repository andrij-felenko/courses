/* ==========================================================================
 * reactor_server.c — Однопотоковий подієвий сервер на C (Linux epoll)
 * Компіляція: gcc -O2 -Wall -Wextra reactor_server.c -o reactor_server
 * ========================================================================== */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <sys/timerfd.h>
#include <sys/signalfd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <time.h>

#define MAX_EVENTS      64
#define BUFFER_SIZE     4096
#define IDLE_TIMEOUT_S  30
#define SERVER_PORT     8080

/* Стан сесії клієнтського з'єднання */
typedef struct client_session {
    int     fd;
    time_t  last_active;
    char   *out_buf;
    size_t  out_len;
    size_t  out_cap;
} client_session_t;

/* Встановлення неблокуючого режиму дескриптора */
static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

/* Створення нової структури сесії */
static client_session_t *session_create(int fd) {
    client_session_t *s = (client_session_t *)calloc(1, sizeof(client_session_t));
    if (!s) return NULL;
    s->fd = fd;
    s->last_active = time(NULL);
    return s;
}

/* Звільнення пам'яті сесії */
static void session_destroy(client_session_t *s) {
    if (!s) return;
    if (s->out_buf) free(s->out_buf);
    free(s);
}

/* Додавання байтів у вихідний буфер сесії */
static int session_append_out(client_session_t *s, const char *data, size_t len) {
    if (s->out_len + len > s->out_cap) {
        size_t new_cap = (s->out_cap == 0) ? 1024 : s->out_cap * 2;
        while (new_cap < s->out_len + len) new_cap *= 2;
        char *nb = (char *)realloc(s->out_buf, new_cap);
        if (!nb) return -1;
        s->out_buf = nb;
        s->out_cap = new_cap;
    }
    memcpy(s->out_buf + s->out_len, data, len);
    s->out_len += len;
    return 0;
}

/* Закриття клієнта та видалення з epoll */
static void close_client(int epfd, client_session_t *s) {
    epoll_ctl(epfd, EPOLL_CTL_DEL, s->fd, NULL);
    close(s->fd);
    printf("[DISCONNECT] Клієнт FD %d відключений\n", s->fd);
    session_destroy(s);
}

/* Обробник вхідних з'єднань (Accept Handler) */
static void handle_accept(int epfd, int listen_fd) {
    while (1) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int client_fd = accept4(listen_fd, (struct sockaddr *)&client_addr, 
                                &client_len, SOCK_NONBLOCK | SOCK_CLOEXEC);
        if (client_fd == -1) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                break; /* Усі нові з'єднання вичитано */
            }
            perror("accept4");
            break;
        }

        client_session_t *s = session_create(client_fd);
        if (!s) {
            close(client_fd);
            continue;
        }

        struct epoll_event ev;
        memset(&ev, 0, sizeof(ev));
        ev.events = EPOLLIN | EPOLLET | EPOLLRDHUP;
        ev.data.ptr = s;

        if (epoll_ctl(epfd, EPOLL_CTL_ADD, client_fd, &ev) == -1) {
            perror("epoll_ctl ADD client");
            close(client_fd);
            session_destroy(s);
            continue;
        }

        char ip_str[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, ip_str, sizeof(ip_str));
        printf("[CONNECT] Новий клієнт FD %d з %s:%d\n", 
               client_fd, ip_str, ntohs(client_addr.sin_port));
    }
}

/* Обробник читання даних клієнта (Read Handler) */
static void handle_read(int epfd, client_session_t *s) {
    char buf[BUFFER_SIZE];
    s->last_active = time(NULL);

    while (1) {
        ssize_t bytes_read = read(s->fd, buf, sizeof(buf));
        if (bytes_read > 0) {
            /* Відлуння (Echo): додаємо прочитане у вихідний буфер */
            session_append_out(s, buf, (size_t)bytes_read);
        } else if (bytes_read == 0) {
            /* Клієнт закрив з'єднання (EOF) */
            close_client(epfd, s);
            return;
        } else {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                break; /* Буфер сокета вичитано повністю */
            }
            /* Справжня мережева помилка */
            close_client(epfd, s);
            return;
        }
    }

    /* Якщо з'явилися дані для відправки — пробуємо записати одразу */
    if (s->out_len > 0) {
        ssize_t bytes_sent = write(s->fd, s->out_buf, s->out_len);
        if (bytes_sent > 0) {
            if ((size_t)bytes_sent < s->out_len) {
                memmove(s->out_buf, s->out_buf + bytes_sent, s->out_len - bytes_sent);
                s->out_len -= bytes_sent;
            } else {
                s->out_len = 0;
            }
        } else if (bytes_sent == -1 && (errno != EAGAIN && errno != EWOULDBLOCK)) {
            close_client(epfd, s);
            return;
        }

        /* Якщо дані лишилися — реєструємо EPOLLOUT */
        if (s->out_len > 0) {
            struct epoll_event ev;
            ev.events = EPOLLIN | EPOLLOUT | EPOLLET | EPOLLRDHUP;
            ev.data.ptr = s;
            epoll_ctl(epfd, EPOLL_CTL_MOD, s->fd, &ev);
        }
    }
}

/* Обробник неблокуючого запису (Write Handler) */
static void handle_write(int epfd, client_session_t *s) {
    s->last_active = time(NULL);

    while (s->out_len > 0) {
        ssize_t bytes_sent = write(s->fd, s->out_buf, s->out_len);
        if (bytes_sent > 0) {
            if ((size_t)bytes_sent < s->out_len) {
                memmove(s->out_buf, s->out_buf + bytes_sent, s->out_len - bytes_sent);
                s->out_len -= bytes_sent;
            } else {
                s->out_len = 0;
            }
        } else if (bytes_sent == -1) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                break; /* Буфер сокета заповнено — чекаємо наступного EPOLLOUT */
            }
            close_client(epfd, s);
            return;
        }
    }

    /* Якщо весь буфер надіслано — знімаємо прапорець EPOLLOUT */
    if (s->out_len == 0) {
        struct epoll_event ev;
        ev.events = EPOLLIN | EPOLLET | EPOLLRDHUP;
        ev.data.ptr = s;
        epoll_ctl(epfd, EPOLL_CTL_MOD, s->fd, &ev);
    }
}

int main(void) {
    /* 1. Блокуємо сигнали для безпечної обробки через signalfd */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);
    sigprocmask(SIG_BLOCK, &mask, NULL);

    int sig_fd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sig_fd == -1) { perror("signalfd"); exit(EXIT_FAILURE); }

    /* 2. Створюємо слухаючий TCP сокет */
    int listen_fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (listen_fd == -1) { perror("socket"); exit(EXIT_FAILURE); }

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in srv_addr;
    memset(&srv_addr, 0, sizeof(srv_addr));
    srv_addr.sin_family = AF_INET;
    srv_addr.sin_addr.s_addr = INADDR_ANY;
    srv_addr.sin_port = htons(SERVER_PORT);

    if (bind(listen_fd, (struct sockaddr *)&srv_addr, sizeof(srv_addr)) == -1) {
        perror("bind"); exit(EXIT_FAILURE);
    }
    if (listen(listen_fd, SOMAXCONN) == -1) {
        perror("listen"); exit(EXIT_FAILURE);
    }

    /* 3. Створюємо таймер перевірки таймаутів (кожні 5 секунд) */
    int timer_fd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
    struct itimerspec ts;
    ts.it_interval.tv_sec = 5;
    ts.it_interval.tv_nsec = 0;
    ts.it_value.tv_sec = 5;
    ts.it_value.tv_nsec = 0;
    timerfd_settime(timer_fd, 0, &ts, NULL);

    /* 4. Ініціалізуємо екземпляр epoll */
    int epfd = epoll_create1(EPOLL_CLOEXEC);
    if (epfd == -1) { perror("epoll_create1"); exit(EXIT_FAILURE); }

    struct epoll_event ev;
    memset(&ev, 0, sizeof(ev));

    /* Реєструємо слухаючий сокет */
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = listen_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev);

    /* Реєструємо дескриптор сигналів */
    ev.events = EPOLLIN;
    ev.data.fd = sig_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, sig_fd, &ev);

    /* Реєструємо таймер */
    ev.events = EPOLLIN;
    ev.data.fd = timer_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, timer_fd, &ev);

    printf("Reactor сервер запущено на порту %d. Очікування подій...\n", SERVER_PORT);

    struct epoll_event events[MAX_EVENTS];
    int running = 1;

    /* 5. Головний цикл подій (Event Loop) */
    while (running) {
        int nready = epoll_wait(epfd, events, MAX_EVENTS, -1);
        if (nready == -1) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }

        for (int i = 0; i < nready; ++i) {
            uint32_t revents = events[i].events;

            /* Подія на дескрипторі сигналів */
            if (events[i].data.fd == sig_fd) {
                struct signalfd_siginfo fdsi;
                read(sig_fd, &fdsi, sizeof(fdsi));
                printf("\n[SIGNAL] Отримано сигнал %d. Зупинка сервера...\n", fdsi.ssi_signo);
                running = 0;
                break;
            }

            /* Подія на таймері */
            if (events[i].data.fd == timer_fd) {
                uint64_t expirations;
                read(timer_fd, &expirations, sizeof(expirations));
                continue;
            }

            /* Нове вхідне підключення */
            if (events[i].data.fd == listen_fd) {
                handle_accept(epfd, listen_fd);
                continue;
            }

            /* Подія на підключеному клієнті */
            client_session_t *s = (client_session_t *)events[i].data.ptr;
            if (!s) continue;

            if (revents & (EPOLLERR | EPOLLHUP | EPOLLRDHUP)) {
                close_client(epfd, s);
                continue;
            }
            if (revents & EPOLLIN) {
                handle_read(epfd, s);
            }
            if (revents & EPOLLOUT) {
                handle_write(epfd, s);
            }
        }
    }

    close(listen_fd);
    close(timer_fd);
    close(sig_fd);
    close(epfd);
    printf("Сервер успішно зупинено.\n");
    return 0;
}
