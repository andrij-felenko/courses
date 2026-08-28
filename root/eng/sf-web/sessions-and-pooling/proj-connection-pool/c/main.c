#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <poll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <pthread.h>

#define MAX_POOL_CAPACITY 16

typedef struct {
    int fd;
    time_t last_used;
} PooledSocket;

typedef struct {
    char host[128];
    int port;
    int max_size;
    int idle_timeout_sec;

    PooledSocket idle_stack[MAX_POOL_CAPACITY];
    int idle_count;
    int active_leased;

    pthread_mutex_t lock;
    pthread_cond_t available_cv;
} ConnectionPool;

static int create_tcp_socket(const char *host, int port) {
    struct addrinfo hints, *res, *p;
    char port_str[16];
    snprintf(port_str, sizeof(port_str), "%d", port);

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if (getaddrinfo(host, port_str, &hints, &res) != 0) {
        return -1;
    }

    int sockfd = -1;
    for (p = res; p != NULL; p = p->ai_next) {
        sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (sockfd < 0) continue;

        if (connect(sockfd, p->ai_addr, p->ai_addrlen) == 0) {
            break;
        }
        close(sockfd);
        sockfd = -1;
    }
    freeaddrinfo(res);
    return sockfd;
}

static int is_socket_healthy(int fd) {
    struct pollfd pfd;
    pfd.fd = fd;
    pfd.events = POLLIN | POLLHUP | POLLERR;
    pfd.revents = 0;

    int ret = poll(&pfd, 1, 0); // Неблокуюча перевірка
    if (ret < 0) return 0;
    if (ret > 0) {
        char buf[1];
        ssize_t n = recv(fd, buf, 1, MSG_PEEK | MSG_DONTWAIT);
        if (n <= 0) return 0; // EOF або помилка зв'язку
    }
    return 1;
}

int pool_init(ConnectionPool *pool, const char *host, int port, int max_size, int idle_timeout) {
    strncpy(pool->host, host, sizeof(pool->host) - 1);
    pool->port = port;
    pool->max_size = (max_size > MAX_POOL_CAPACITY) ? MAX_POOL_CAPACITY : max_size;
    pool->idle_timeout_sec = idle_timeout;
    pool->idle_count = 0;
    pool->active_leased = 0;

    if (pthread_mutex_init(&pool->lock, NULL) != 0) return -1;
    if (pthread_cond_init(&pool->available_cv, NULL) != 0) {
        pthread_mutex_destroy(&pool->lock);
        return -1;
    }
    return 0;
}

int pool_acquire(ConnectionPool *pool, int timeout_ms) {
    pthread_mutex_lock(&pool->lock);
    time_t now = time(NULL);

    while (1) {
        // 1. Спроба взяти сокет зі стека LIFO
        while (pool->idle_count > 0) {
            PooledSocket item = pool->idle_stack[--pool->idle_count];

            // Перевірка таймауту бездіяльності
            if (now - item.last_used > pool->idle_timeout_sec) {
                close(item.fd);
                continue;
            }

            // Перевірка працездатності каналу
            if (!is_socket_healthy(item.fd)) {
                close(item.fd);
                continue;
            }

            pool->active_leased++;
            pthread_mutex_unlock(&pool->lock);
            return item.fd;
        }

        // 2. Створення нового сокета за наявності вільного ліміту
        if (pool->active_leased < pool->max_size) {
            pool->active_leased++;
            pthread_mutex_unlock(&pool->lock);

            int new_fd = create_tcp_socket(pool->host, pool->port);
            if (new_fd < 0) {
                pthread_mutex_lock(&pool->lock);
                pool->active_leased--;
                pthread_cond_signal(&pool->available_cv);
                pthread_mutex_unlock(&pool->lock);
                return -1;
            }
            return new_fd;
        }

        // 3. Очікування вивільнення сокета на condition variable
        struct timespec ts;
        clock_gettime(CLOCK_REALTIME, &ts);
        ts.tv_sec += timeout_ms / 1000;
        ts.tv_nsec += (timeout_ms % 1000) * 1000000L;
        if (ts.tv_nsec >= 1000000000L) {
            ts.tv_sec += 1;
            ts.tv_nsec -= 1000000000L;
        }

        int wait_res = pthread_cond_timedwait(&pool->available_cv, &pool->lock, &ts);
        if (wait_res == ETIMEDOUT) {
            pthread_mutex_unlock(&pool->lock);
            return -1;
        }
        now = time(NULL);
    }
}

void pool_release(ConnectionPool *pool, int fd, int is_broken) {
    if (fd < 0) return;

    pthread_mutex_lock(&pool->lock);
    pool->active_leased--;

    if (is_broken) {
        close(fd);
    } else {
        if (pool->idle_count < pool->max_size) {
            pool->idle_stack[pool->idle_count].fd = fd;
            pool->idle_stack[pool->idle_count].last_used = time(NULL);
            pool->idle_count++;
        } else {
            close(fd);
        }
    }

    pthread_cond_signal(&pool->available_cv);
    pthread_mutex_unlock(&pool->lock);
}

void pool_destroy(ConnectionPool *pool) {
    pthread_mutex_lock(&pool->lock);
    for (int i = 0; i < pool->idle_count; ++i) {
        close(pool->idle_stack[i].fd);
    }
    pool->idle_count = 0;
    pool->active_leased = 0;
    pthread_mutex_unlock(&pool->lock);

    pthread_mutex_destroy(&pool->lock);
    pthread_cond_destroy(&pool->available_cv);
}
