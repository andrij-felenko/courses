#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <netdb.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

#define MAX_EVENTS 1024
#define BUFFER_SIZE 16384
#define LISTEN_PORT 8080
#define UPSTREAM_HOST "127.0.0.1"
#define UPSTREAM_PORT 8000

typedef enum {
    STATE_CONNECTING_UPSTREAM,
    STATE_STREAMING
} SessionState;

typedef struct {
    int client_fd;
    int upstream_fd;
    SessionState state;
    char client_to_up_buf[BUFFER_SIZE];
    size_t c2u_len;
    char up_to_client_buf[BUFFER_SIZE];
    size_t u2c_len;
    char client_ip[INET_ADDRSTRLEN];
} ProxySession;

static int make_socket_non_blocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

static void close_session(int epoll_fd, ProxySession *session) {
    if (!session) return;
    if (session->client_fd >= 0) {
        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, session->client_fd, NULL);
        close(session->client_fd);
    }
    if (session->upstream_fd >= 0) {
        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, session->upstream_fd, NULL);
        close(session->upstream_fd);
    }
    free(session);
}

static int create_and_bind_listener(int port) {
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd == -1) return -1;

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);

    if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
        close(listen_fd);
        return -1;
    }
    if (make_socket_non_blocking(listen_fd) == -1) {
        close(listen_fd);
        return -1;
    }
    if (listen(listen_fd, SOMAXCONN) == -1) {
        close(listen_fd);
        return -1;
    }
    return listen_fd;
}

static int connect_to_upstream(const char *host, int port) {
    int up_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (up_fd == -1) return -1;

    if (make_socket_non_blocking(up_fd) == -1) {
        close(up_fd);
        return -1;
    }

    struct sockaddr_in up_addr;
    memset(&up_addr, 0, sizeof(up_addr));
    up_addr.sin_family = AF_INET;
    up_addr.sin_port = htons(port);
    inet_pton(AF_INET, host, &up_addr.sin_addr);

    int res = connect(up_fd, (struct sockaddr *)&up_addr, sizeof(up_addr));
    if (res == -1 && errno != EINPROGRESS) {
        close(up_fd);
        return -1;
    }
    return up_fd;
}

int main(void) {
    // Ігноруємо сигнал SIGPIPE, щоб уникнути аварійного завершення процесу при записі в закритий сокет
    signal(SIGPIPE, SIG_IGN);

    int listen_fd = create_and_bind_listener(LISTEN_PORT);
    if (listen_fd == -1) {
        perror("Помилка створення слухаючого сокета");
        return 1;
    }

    int epoll_fd = epoll_create1(0);
    if (epoll_fd == -1) {
        perror("epoll_create1");
        close(listen_fd);
        return 1;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.ptr = NULL; // NULL вказує на слухаючий сокет
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listen_fd, &ev) == -1) {
        perror("epoll_ctl listen_fd");
        close(listen_fd);
        close(epoll_fd);
        return 1;
    }

    struct epoll_event events[MAX_EVENTS];
    printf("Зворотний проксі запущено на порту %d -> апстрім %s:%d\n",
           LISTEN_PORT, UPSTREAM_HOST, UPSTREAM_PORT);

    while (1) {
        int n_fds = epoll_wait(epoll_fd, events, MAX_EVENTS, -1);
        if (n_fds == -1) {
            if (errno == EINTR) continue;
            break;
        }

        for (int i = 0; i < n_fds; ++i) {
            if (events[i].data.ptr == NULL) {
                // Прийом усіх очікуючих клієнтських з'єднань
                while (1) {
                    struct sockaddr_in client_addr;
                    socklen_t client_len = sizeof(client_addr);
                    int client_fd = accept(listen_fd, (struct sockaddr *)&client_addr, &client_len);
                    if (client_fd == -1) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                        perror("accept");
                        break;
                    }

                    make_socket_non_blocking(client_fd);

                    int up_fd = connect_to_upstream(UPSTREAM_HOST, UPSTREAM_PORT);
                    if (up_fd == -1) {
                        close(client_fd);
                        continue;
                    }

                    ProxySession *session = (ProxySession *)calloc(1, sizeof(ProxySession));
                    if (!session) {
                        close(client_fd);
                        close(up_fd);
                        continue;
                    }
                    session->client_fd = client_fd;
                    session->upstream_fd = up_fd;
                    session->state = STATE_CONNECTING_UPSTREAM;
                    inet_ntop(AF_INET, &client_addr.sin_addr, session->client_ip, sizeof(session->client_ip));

                    struct epoll_event ev_client, ev_up;
                    ev_client.events = EPOLLIN | EPOLLRDHUP | EPOLLERR;
                    ev_client.data.ptr = session;
                    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &ev_client);

                    ev_up.events = EPOLLOUT | EPOLLRDHUP | EPOLLERR;
                    ev_up.data.ptr = session;
                    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, up_fd, &ev_up);
                }
            } else {
                ProxySession *session = (ProxySession *)events[i].data.ptr;
                uint32_t evs = events[i].events;

                if (evs & (EPOLLRDHUP | EPOLLERR | EPOLLHUP)) {
                    close_session(epoll_fd, session);
                    continue;
                }

                if (session->state == STATE_CONNECTING_UPSTREAM) {
                    int err = 0;
                    socklen_t len = sizeof(err);
                    if (getsockopt(session->upstream_fd, SOL_SOCKET, SO_ERROR, &err, &len) < 0 || err != 0) {
                        close_session(epoll_fd, session);
                        continue;
                    }
                    session->state = STATE_STREAMING;
                    struct epoll_event ev_up;
                    ev_up.events = EPOLLIN | EPOLLRDHUP | EPOLLERR;
                    ev_up.data.ptr = session;
                    epoll_ctl(epoll_fd, EPOLL_CTL_MOD, session->upstream_fd, &ev_up);
                }

                // Перекачування байтів від клієнта до апстріму
                char buf[BUFFER_SIZE];
                ssize_t bytes_read = read(session->client_fd, buf, sizeof(buf));
                if (bytes_read > 0) {
                    ssize_t sent = write(session->upstream_fd, buf, (size_t)bytes_read);
                    (void)sent;
                } else if (bytes_read == 0 || (bytes_read == -1 && errno != EAGAIN)) {
                    close_session(epoll_fd, session);
                    continue;
                }

                // Перекачування байтів від апстріму до клієнта
                ssize_t up_read = read(session->upstream_fd, buf, sizeof(buf));
                if (up_read > 0) {
                    ssize_t sent = write(session->client_fd, buf, (size_t)up_read);
                    (void)sent;
                } else if (up_read == 0 || (up_read == -1 && errno != EAGAIN)) {
                    close_session(epoll_fd, session);
                    continue;
                }
            }
        }
    }

    close(listen_fd);
    close(epoll_fd);
    return 0;
}
