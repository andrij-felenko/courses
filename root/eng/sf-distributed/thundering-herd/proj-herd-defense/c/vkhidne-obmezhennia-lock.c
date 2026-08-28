/* C11 server worker with SO_REUSEPORT and Token Bucket rate limiter */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <time.h>
#include <pthread.h>

#define MAX_EVENTS 64
#define PORT 8080

typedef struct {
    double capacity;
    double tokens;
    double refill_rate;
    struct timespec last_refill;
    pthread_mutex_t lock;
} TokenBucket;

void tb_init(TokenBucket *tb, double capacity, double rate) {
    tb->capacity = capacity;
    tb->tokens = capacity;
    tb->refill_rate = rate;
    clock_gettime(CLOCK_MONOTONIC, &tb->last_refill);
    pthread_mutex_init(&tb->lock, NULL);
}

bool tb_consume(TokenBucket *tb) {
    pthread_mutex_lock(&tb->lock);
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    double elapsed = (now.tv_sec - tb->last_refill.tv_sec) +
                     (now.tv_nsec - tb->last_refill.tv_nsec) / 1e9;
    tb->last_refill = now;

    tb->tokens += elapsed * tb->refill_rate;
    if (tb->tokens > tb->capacity) {
        tb->tokens = tb->capacity;
    }

    bool allowed = false;
    if (tb->tokens >= 1.0) {
        tb->tokens -= 1.0;
        allowed = true;
    }
    pthread_mutex_unlock(&tb->lock);
    return allowed;
}

int create_reuseport_listener(int port) {
    int listen_fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);
    if (listen_fd < 0) return -1;

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);

    if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(listen_fd);
        return -1;
    }

    if (listen(listen_fd, 4096) < 0) {
        close(listen_fd);
        return -1;
    }

    return listen_fd;
}
