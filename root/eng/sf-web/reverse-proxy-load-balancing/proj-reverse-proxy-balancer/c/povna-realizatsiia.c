#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <time.h>

#define MAX_EVENTS 64
#define BUFFER_SIZE 16384
#define MAX_BACKENDS 8
#define HEALTH_CHECK_INTERVAL_SEC 5
#define UNHEALTHY_THRESHOLD 3
#define HEALTHY_THRESHOLD 2

typedef struct {
    char ip[INET_ADDRSTRLEN];
    int port;
    int active_connections;
    int is_healthy;
    int consecutive_successes;
    int consecutive_failures;
} backend_node_t;

typedef struct {
    backend_node_t backends[MAX_BACKENDS];
    int count;
    int round_robin_idx;
} load_balancer_t;

typedef enum {
    CONN_STATE_READ_CLIENT,
    CONN_STATE_WRITE_BACKEND,
    CONN_STATE_READ_BACKEND,
    CONN_STATE_WRITE_CLIENT
} conn_state_t;

typedef struct {
    int client_fd;
    int backend_fd;
    int backend_idx;
    conn_state_t state;
    char client_buffer[BUFFER_SIZE];
    size_t client_bytes_read;
    char backend_buffer[BUFFER_SIZE];
    size_t backend_bytes_read;
    size_t bytes_written;
} proxy_conn_t;

static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

static load_balancer_t g_lb;

void init_load_balancer(load_balancer_t *lb) {
    lb->count = 0;
    lb->round_robin_idx = 0;
}

int add_backend(load_balancer_t *lb, const char *ip, int port) {
    if (lb->count >= MAX_BACKENDS) return -1;
    backend_node_t *node = &lb->backends[lb->count++];
    strncpy(node->ip, ip, sizeof(node->ip) - 1);
    node->port = port;
    node->active_connections = 0;
    node->is_healthy = 1;
    node->consecutive_successes = HEALTHY_THRESHOLD;
    node->consecutive_failures = 0;
    return 0;
}

/* Вибір бекенда за алгоритмом Least Connections серед здорових вузлів */
int select_backend_least_conn(load_balancer_t *lb) {
    int selected = -1;
    int min_conn = 1000000;
    for (int i = 0; i < lb->count; ++i) {
        if (!lb->backends[i].is_healthy) continue;
        if (lb->backends[i].active_connections < min_conn) {
            min_conn = lb->backends[i].active_connections;
            selected = i;
        }
    }
    return selected;
}

/* Підключення до обраного бекенда у неблокуючому режимі */
int connect_to_backend(const backend_node_t *backend) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    
    int flag = 1;
    setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
    set_nonblocking(fd);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(backend->port);
    inet_pton(AF_INET, backend->ip, &addr.sin_addr);

    int res = connect(fd, (struct sockaddr *)&addr, sizeof(addr));
    if (res < 0 && errno != EINPROGRESS) {
        close(fd);
        return -1;
    }
    return fd;
}

/* Активне зондування здоров'я бекендів через GET /healthz */
void perform_active_health_checks(load_balancer_t *lb) {
    for (int i = 0; i < lb->count; ++i) {
        backend_node_t *node = &lb->backends[i];
        int fd = socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) continue;

        struct timeval tv = { .tv_sec = 1, .tv_usec = 0 };
        setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
        setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(node->port);
        inet_pton(AF_INET, node->ip, &addr.sin_addr);

        int ok = 0;
        if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
            const char req[] = "GET /healthz HTTP/1.1\r\nHost: healthcheck\r\nConnection: close\r\n\r\n";
            if (write(fd, req, sizeof(req) - 1) > 0) {
                char resp[128];
                ssize_t n = read(fd, resp, sizeof(resp) - 1);
                if (n > 0) {
                    resp[n] = '\0';
                    if (strstr(resp, "200 OK") != NULL) {
                        ok = 1;
                    }
                }
            }
        }
        close(fd);

        if (ok) {
            node->consecutive_failures = 0;
            node->consecutive_successes++;
            if (!node->is_healthy && node->consecutive_successes >= HEALTHY_THRESHOLD) {
                node->is_healthy = 1;
            }
        } else {
            node->consecutive_successes = 0;
            node->consecutive_failures++;
            if (node->is_healthy && node->consecutive_failures >= UNHEALTHY_THRESHOLD) {
                node->is_healthy = 0;
            }
        }
    }
}

void close_proxy_connection(int epoll_fd, proxy_conn_t *conn, load_balancer_t *lb) {
    if (conn->client_fd >= 0) {
        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, conn->client_fd, NULL);
        close(conn->client_fd);
    }
    if (conn->backend_fd >= 0) {
        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, conn->backend_fd, NULL);
        close(conn->backend_fd);
        if (conn->backend_idx >= 0 && conn->backend_idx < lb->count) {
            lb->backends[conn->backend_idx].active_connections--;
            if (lb->backends[conn->backend_idx].active_connections < 0) {
                lb->backends[conn->backend_idx].active_connections = 0;
            }
        }
    }
    free(conn);
}

int main(int argc, char *argv[]) {
    int listen_port = (argc > 1) ? atoi(argv[1]) : 8080;
    init_load_balancer(&g_lb);
    add_backend(&g_lb, "127.0.0.1", 8081);
    add_backend(&g_lb, "127.0.0.1", 8082);

    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) return 1;

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    set_nonblocking(listen_fd);

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(listen_port);

    if (bind(listen_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) return 1;
    if (listen(listen_fd, 1024) < 0) return 1;

    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) return 1;

    struct epoll_event ev, events[MAX_EVENTS];
    ev.events = EPOLLIN;
    ev.data.fd = listen_fd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listen_fd, &ev);

    time_t last_health_check = time(NULL);

    while (1) {
        time_t now = time(NULL);
        if (now - last_health_check >= HEALTH_CHECK_INTERVAL_SEC) {
            perform_active_health_checks(&g_lb);
            last_health_check = now;
        }

        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, 1000);
        for (int i = 0; i < nfds; ++i) {
            if (events[i].data.fd == listen_fd) {
                struct sockaddr_in client_addr;
                socklen_t client_len = sizeof(client_addr);
                int client_fd = accept(listen_fd, (struct sockaddr *)&client_addr, &client_len);
                if (client_fd >= 0) {
                    set_nonblocking(client_fd);
                    proxy_conn_t *conn = calloc(1, sizeof(proxy_conn_t));
                    conn->client_fd = client_fd;
                    conn->backend_fd = -1;
                    conn->backend_idx = -1;
                    conn->state = CONN_STATE_READ_CLIENT;

                    struct epoll_event cev;
                    cev.events = EPOLLIN | EPOLLET;
                    cev.data.ptr = conn;
                    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &cev);
                }
            } else {
                proxy_conn_t *conn = (proxy_conn_t *)events[i].data.ptr;
                if (conn->state == CONN_STATE_READ_CLIENT) {
                    ssize_t n = read(conn->client_fd, conn->client_buffer, sizeof(conn->client_buffer) - 1);
                    if (n > 0) {
                        conn->client_bytes_read = n;
                        conn->client_buffer[n] = '\0';

                        int b_idx = select_backend_least_conn(&g_lb);
                        if (b_idx < 0) {
                            const char err503[] = "HTTP/1.1 503 Service Unavailable\r\nContent-Length: 21\r\n\r\nNo Healthy Backends\n";
                            write(conn->client_fd, err503, sizeof(err503) - 1);
                            close_proxy_connection(epoll_fd, conn, &g_lb);
                            continue;
                        }

                        int b_fd = connect_to_backend(&g_lb.backends[b_idx]);
                        if (b_fd < 0) {
                            close_proxy_connection(epoll_fd, conn, &g_lb);
                            continue;
                        }

                        conn->backend_fd = b_fd;
                        conn->backend_idx = b_idx;
                        g_lb.backends[b_idx].active_connections++;
                        conn->state = CONN_STATE_WRITE_BACKEND;

                        struct epoll_event bev;
                        bev.events = EPOLLOUT | EPOLLET;
                        bev.data.ptr = conn;
                        epoll_ctl(epoll_fd, EPOLL_CTL_ADD, b_fd, &bev);
                    } else if (n == 0 || (n < 0 && errno != EAGAIN)) {
                        close_proxy_connection(epoll_fd, conn, &g_lb);
                    }
                } else if (conn->state == CONN_STATE_WRITE_BACKEND) {
                    ssize_t written = write(conn->backend_fd, conn->client_buffer, conn->client_bytes_read);
                    if (written > 0) {
                        conn->state = CONN_STATE_READ_BACKEND;
                        struct epoll_event bev;
                        bev.events = EPOLLIN | EPOLLET;
                        bev.data.ptr = conn;
                        epoll_ctl(epoll_fd, EPOLL_CTL_MOD, conn->backend_fd, &bev);
                    } else if (written < 0 && errno != EAGAIN) {
                        close_proxy_connection(epoll_fd, conn, &g_lb);
                    }
                } else if (conn->state == CONN_STATE_READ_BACKEND) {
                    ssize_t n = read(conn->backend_fd, conn->backend_buffer, sizeof(conn->backend_buffer));
                    if (n > 0) {
                        conn->backend_bytes_read = n;
                        write(conn->client_fd, conn->backend_buffer, conn->backend_bytes_read);
                        close_proxy_connection(epoll_fd, conn, &g_lb);
                    } else if (n == 0 || (n < 0 && errno != EAGAIN)) {
                        close_proxy_connection(epoll_fd, conn, &g_lb);
                    }
                }
            }
        }
    }
    close(listen_fd);
    close(epoll_fd);
    return 0;
}
