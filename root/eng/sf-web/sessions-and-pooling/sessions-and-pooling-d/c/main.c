#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>
#include <pthread.h>

#define POOL_SIZE 8

typedef struct {
    int sockets[POOL_SIZE];
    int top;
    pthread_mutex_t lock;
    pthread_cond_t cond;
} SimpleSocketPool;

void pool_init_c(SimpleSocketPool *p) {
    p->top = 0;
    pthread_mutex_init(&p->lock, NULL);
    pthread_cond_init(&p->cond, NULL);
}

// Перевірка працездатності сокета перед видачею
int is_socket_alive(int fd) {
    struct pollfd pfd = { .fd = fd, .events = POLLIN | POLLHUP | POLLERR, .revents = 0 };
    int res = poll(&pfd, 1, 0);
    if (res < 0) return 0;
    if (res > 0) {
        char buf[1];
        if (recv(fd, buf, 1, MSG_PEEK | MSG_DONTWAIT) <= 0) {
            return 0; // Сокет розірвано віддаленою стороною (EOF)
        }
    }
    return 1;
}

int pool_acquire_c(SimpleSocketPool *p) {
    pthread_mutex_lock(&p->lock);
    while (p->top == 0) {
        pthread_cond_wait(&p->cond, &p->lock);
    }

    int fd = p->sockets[--p->top];
    pthread_mutex_unlock(&p->lock);

    if (!is_socket_alive(fd)) {
        close(fd);
        // За потреби створюється новий сокет викликом connect()
        return -1;
    }
    return fd;
}

void pool_release_c(SimpleSocketPool *p, int fd) {
    pthread_mutex_lock(&p->lock);
    if (p->top < POOL_SIZE) {
        p->sockets[p->top++] = fd;
        pthread_cond_signal(&p->cond);
    } else {
        close(fd); // Переповнення пулу: закриваємо зайвий сокет
    }
    pthread_mutex_unlock(&p->lock);
}
