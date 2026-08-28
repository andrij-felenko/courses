#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>

typedef struct {
    int fd;
    time_t created_at;
    time_t last_used_at;
} PooledConnection;

typedef struct {
    char host[128];
    int port;
    int max_capacity;
    int max_idle_sec;
    int max_life_sec;

    PooledConnection **idle_stack;
    int idle_count;
    int active_count;

    pthread_mutex_t lock;
    pthread_cond_t cond;
    int is_shutdown;
} ConnectionPool;

static int connect_to_host(const char *host, int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons((uint16_t)port);
    if (inet_pton(AF_INET, host, &addr.sin_addr) <= 0) {
        close(fd);
        return -1;
    }

    if (connect(fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

static int is_connection_alive(int fd) {
    char probe;
    ssize_t r = recv(fd, &probe, 1, MSG_PEEK | MSG_DONTWAIT);
    if (r == 0) return 0; // Отримано FIN від сервера
    if (r < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) return 1; // Буфер чистий, з'єднання живе
        return 0; // Апаратна помилка або RST
    }
    return 0; // Неочікувані залишковий трафік
}

ConnectionPool* pool_create(const char *host, int port, int capacity, int max_idle, int max_life) {
    ConnectionPool *p = (ConnectionPool*)calloc(1, sizeof(ConnectionPool));
    if (!p) return NULL;

    strncpy(p->host, host, sizeof(p->host) - 1);
    p->port = port;
    p->max_capacity = capacity;
    p->max_idle_sec = max_idle;
    p->max_life_sec = max_life;

    p->idle_stack = (PooledConnection**)malloc(sizeof(PooledConnection*) * capacity);
    p->idle_count = 0;
    p->active_count = 0;
    p->is_shutdown = 0;

    pthread_mutex_init(&p->lock, NULL);
    pthread_cond_init(&p->cond, NULL);
    return p;
}

PooledConnection* pool_acquire(ConnectionPool *p, int timeout_sec) {
    pthread_mutex_lock(&p->lock);
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += timeout_sec;

    while (1) {
        if (p->is_shutdown) {
            pthread_mutex_unlock(&p->lock);
            return NULL;
        }

        // 1. Спроба взяти готове з'єднання з вершини стека (LIFO)
        time_t now = time(NULL);
        while (p->idle_count > 0) {
            PooledConnection *conn = p->idle_stack[--p->idle_count];
            
            // Перевірка перевищення лімітів часу
            int expired = ((now - conn->last_used_at) > p->max_idle_sec) ||
                          ((now - conn->created_at) > p->max_life_sec);

            if (!expired && is_connection_alive(conn->fd)) {
                p->active_count++;
                pthread_mutex_unlock(&p->lock);
                return conn;
            }

            // З'єднання застаріло або закрите сервером — знищуємо
            close(conn->fd);
            free(conn);
        }

        // 2. Якщо вільних немає, але ліміт ємності не вичерпано — створюємо новий сокет
        if (p->active_count < p->max_capacity) {
            p->active_count++;
            pthread_mutex_unlock(&p->lock);

            // Мережевий виклик connect виконується ПОЗА блокуванням м'ютекса
            int fd = connect_to_host(p->host, p->port);
            if (fd < 0) {
                pthread_mutex_lock(&p->lock);
                p->active_count--;
                pthread_cond_signal(&p->cond);
                pthread_mutex_unlock(&p->lock);
                return NULL;
            }

            PooledConnection *conn = (PooledConnection*)malloc(sizeof(PooledConnection));
            conn->fd = fd;
            conn->created_at = time(NULL);
            conn->last_used_at = conn->created_at;
            return conn;
        }

        // 3. Усі слоти зайняті — очікуємо звільнення іншим потоком
        int rc = pthread_cond_timedwait(&p->cond, &p->lock, &ts);
        if (rc == ETIMEDOUT) {
            pthread_mutex_unlock(&p->lock);
            return NULL;
        }
    }
}

void pool_release(ConnectionPool *p, PooledConnection *conn, int is_broken) {
    if (!conn) return;

    pthread_mutex_lock(&p->lock);
    p->active_count--;

    time_t now = time(NULL);
    int expired = ((now - conn->created_at) > p->max_life_sec);

    if (is_broken || expired || p->is_shutdown || !is_connection_alive(conn->fd)) {
        close(conn->fd);
        free(conn);
    } else {
        conn->last_used_at = now;
        p->idle_stack[p->idle_count++] = conn;
    }

    pthread_cond_signal(&p->cond);
    pthread_mutex_unlock(&p->lock);
}

void pool_destroy(ConnectionPool *p) {
    if (!p) return;

    pthread_mutex_lock(&p->lock);
    p->is_shutdown = 1;
    pthread_cond_broadcast(&p->cond);

    for (int i = 0; i < p->idle_count; ++i) {
        close(p->idle_stack[i]->fd);
        free(p->idle_stack[i]);
    }
    p->idle_count = 0;
    pthread_mutex_unlock(&p->lock);

    pthread_mutex_destroy(&p->lock);
    pthread_cond_destroy(&p->cond);
    free(p->idle_stack);
    free(p);
}
