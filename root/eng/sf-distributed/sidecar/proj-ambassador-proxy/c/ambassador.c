/* ambassador.c — Високопродуктивний вихідний проксі-посол мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <fcntl.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

#define LOCAL_PORT 8081
#define UPSTREAM_IP "127.0.0.1"
#define UPSTREAM_PORT 9000
#define BUFFER_SIZE 8192
#define MAX_RETRIES 3
#define BASE_BACKOFF_MS 50
#define FAILURE_THRESHOLD 5
#define RECOVERY_TIMEOUT_SEC 10

typedef enum {
    CB_CLOSED = 0,
    CB_OPEN,
    CB_HALF_OPEN
} cb_state_t;

typedef struct {
    cb_state_t state;
    int failure_count;
    time_t last_state_change;
} circuit_breaker_t;

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

static void sleep_ms_with_jitter(int ms) {
    int jitter = rand() % 20;
    struct timespec ts;
    ts.tv_sec = (ms + jitter) / 1000;
    ts.tv_nsec = ((ms + jitter) % 1000) * 1000000L;
    nanosleep(&ts, NULL);
}

static int cb_allow_request(circuit_breaker_t *cb) {
    time_t now = time(NULL);
    if (cb->state == CB_OPEN) {
        if (now - cb->last_state_change >= RECOVERY_TIMEOUT_SEC) {
            cb->state = CB_HALF_OPEN;
            cb->last_state_change = now;
            return 1; /* Пробний запит у напіввідкритому стані */
        }
        return 0; /* Запобіжник розімкнутий */
    }
    return 1;
}

static void cb_record_success(circuit_breaker_t *cb) {
    cb->failure_count = 0;
    cb->state = CB_CLOSED;
}

static void cb_record_failure(circuit_breaker_t *cb) {
    cb->failure_count++;
    if (cb->failure_count >= FAILURE_THRESHOLD || cb->state == CB_HALF_OPEN) {
        cb->state = CB_OPEN;
        cb->last_state_change = time(NULL);
    }
}

static int connect_upstream(const char *ip, int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;

    int flag = 1;
    setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, (char *)&flag, sizeof(int));

    /* Встановлення таймауту на передачу та прийом */
    struct timeval tv = { .tv_sec = 2, .tv_usec = 0 };
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof(tv));
    setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, (const char*)&tv, sizeof(tv));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &addr.sin_addr);

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

static void proxy_traffic(int client_fd, circuit_breaker_t *cb) {
    char buf[BUFFER_SIZE];
    ssize_t n_read = read(client_fd, buf, sizeof(buf));
    if (n_read <= 0) {
        close(client_fd);
        return;
    }

    if (!cb_allow_request(cb)) {
        const char *err_resp = "HTTP/1.1 503 Service Unavailable (Circuit Breaker Open)\r\nContent-Length: 0\r\n\r\n";
        (void)write(client_fd, err_resp, strlen(err_resp));
        close(client_fd);
        return;
    }

    int upstream_fd = -1;
    int attempt = 0;
    int success = 0;

    while (attempt < MAX_RETRIES && !success && g_running) {
        upstream_fd = connect_upstream(UPSTREAM_IP, UPSTREAM_PORT);
        if (upstream_fd >= 0) {
            if (write(upstream_fd, buf, n_read) == n_read) {
                ssize_t up_read = read(upstream_fd, buf, sizeof(buf));
                if (up_read > 0) {
                    (void)write(client_fd, buf, up_read);
                    success = 1;
                }
            }
            close(upstream_fd);
        }

        if (!success) {
            attempt++;
            if (attempt < MAX_RETRIES) {
                int backoff = BASE_BACKOFF_MS * (1 << attempt);
                sleep_ms_with_jitter(backoff);
            }
        }
    }

    if (success) {
        cb_record_success(cb);
    } else {
        cb_record_failure(cb);
        const char *err_resp = "HTTP/1.1 504 Gateway Timeout (Upstream Failed)\r\nContent-Length: 0\r\n\r\n";
        (void)write(client_fd, err_resp, strlen(err_resp));
    }

    close(client_fd);
}

int main(void) {
    srand((unsigned int)time(NULL));

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT, &sa, NULL);
    signal(SIGPIPE, SIG_IGN);

    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket");
        return 1;
    }

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in laddr;
    memset(&laddr, 0, sizeof(laddr));
    laddr.sin_family = AF_INET;
    laddr.sin_port = htons(LOCAL_PORT);
    inet_pton(AF_INET, "127.0.0.1", &laddr.sin_addr);

    if (bind(listen_fd, (struct sockaddr *)&laddr, sizeof(laddr)) < 0) {
        perror("bind");
        close(listen_fd);
        return 1;
    }

    if (listen(listen_fd, 128) < 0) {
        perror("listen");
        close(listen_fd);
        return 1;
    }

    circuit_breaker_t cb = { .state = CB_CLOSED, .failure_count = 0, .last_state_change = 0 };
    printf("[Ambassador] Слухач активний на 127.0.0.1:%d, проксування до %s:%d\n",
           LOCAL_PORT, UPSTREAM_IP, UPSTREAM_PORT);

    while (g_running) {
        struct sockaddr_in caddr;
        socklen_t clen = sizeof(caddr);
        int client_fd = accept(listen_fd, (struct sockaddr *)&caddr, &clen);
        if (client_fd < 0) {
            if (errno == EINTR) break;
            continue;
        }
        proxy_traffic(client_fd, &cb);
    }

    printf("[Ambassador] Зупинка проксі за сигналом SIGTERM. Закриття ресурсів.\n");
    close(listen_fd);
    return 0;
}
