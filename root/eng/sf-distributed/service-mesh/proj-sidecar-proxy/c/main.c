#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <stdbool.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define LISTEN_PORT 15001
#define BUFFER_SIZE 16384
#define MAX_UPSTREAMS 8
#define MAX_CONSECUTIVE_5XX 3
#define EJECTION_DURATION_SEC 10

typedef struct {
    char host[64];
    int port;
    int consecutive_5xx;
    time_t ejected_until;
} UpstreamNode;

typedef struct {
    UpstreamNode nodes[MAX_UPSTREAMS];
    size_t count;
    size_t rr_index;
} UpstreamPool;

static UpstreamPool g_pool;

void init_upstream_pool(void) {
    g_pool.count = 0;
    g_pool.rr_index = 0;
}

bool add_upstream(const char* host, int port) {
    if (g_pool.count >= MAX_UPSTREAMS) return false;
    UpstreamNode* node = &g_pool.nodes[g_pool.count++];
    strncpy(node->host, host, sizeof(node->host) - 1);
    node->host[sizeof(node->host) - 1] = '\0';
    node->port = port;
    node->consecutive_5xx = 0;
    node->ejected_until = 0;
    return true;
}

int select_healthy_upstream(void) {
    time_t now = time(NULL);
    size_t checked = 0;

    while (checked < g_pool.count) {
        size_t idx = g_pool.rr_index % g_pool.count;
        g_pool.rr_index = (g_pool.rr_index + 1) % g_pool.count;
        checked++;

        UpstreamNode* node = &g_pool.nodes[idx];
        if (node->ejected_until > 0) {
            if (now >= node->ejected_until) {
                /* Термін виключення минув: пробне повернення вузла в пул */
                node->ejected_until = 0;
                node->consecutive_5xx = 0;
                printf("[CB] Вузол %s:%d повернуто до пулу після охолодження\n", node->host, node->port);
                return (int)idx;
            }
            continue; /* Вузол у стані ізоляції */
        }
        return (int)idx;
    }
    return -1; /* Усі бекенди виключені або пул порожній */
}

void record_upstream_result(int idx, int status_code) {
    if (idx < 0 || (size_t)idx >= g_pool.count) return;
    UpstreamNode* node = &g_pool.nodes[idx];

    if (status_code >= 500 && status_code <= 599) {
        node->consecutive_5xx++;
        printf("[OUTLIER] Вузол %s:%d повернув помилку %d (підряд: %d/%d)\n",
               node->host, node->port, status_code, node->consecutive_5xx, MAX_CONSECUTIVE_5XX);

        if (node->consecutive_5xx >= MAX_CONSECUTIVE_5XX) {
            node->ejected_until = time(NULL) + EJECTION_DURATION_SEC;
            printf("[CIRCUIT_BREAKER] Вузол %s:%d ізольовано на %d секунд!\n",
                   node->host, node->port, EJECTION_DURATION_SEC);
        }
    } else if (status_code >= 200 && status_code < 500) {
        /* Успішний статус скидає лічильник послідовних збоїв */
        node->consecutive_5xx = 0;
    }
}

int connect_to_upstream(const char* host, int port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return -1;

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    if (inet_pton(AF_INET, host, &serv_addr.sin_addr) <= 0) {
        close(sock);
        return -1;
    }

    struct timeval tv = { .tv_sec = 2, .tv_usec = 0 };
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        close(sock);
        return -1;
    }
    return sock;
}

int parse_http_status(const char* response_buf, size_t len) {
    if (len < 12) return 0;
    if (strncmp(response_buf, "HTTP/1.", 7) != 0) return 0;
    const char* p = response_buf + 8;
    while (*p == ' ' && (size_t)(p - response_buf) < len) p++;
    return atoi(p);
}

void handle_client(int client_fd) {
    char buffer[BUFFER_SIZE];
    ssize_t bytes_read = read(client_fd, buffer, sizeof(buffer) - 1);
    if (bytes_read <= 0) {
        close(client_fd);
        return;
    }
    buffer[bytes_read] = '\0';

    int upstream_idx = select_healthy_upstream();
    if (upstream_idx < 0) {
        const char* err_503 = 
            "HTTP/1.1 503 Service Unavailable\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 42\r\n\r\n"
            "Service Mesh: No healthy upstream hosts\n";
        write(client_fd, err_503, strlen(err_503));
        close(client_fd);
        return;
    }

    UpstreamNode* node = &g_pool.nodes[upstream_idx];
    int upstream_fd = connect_to_upstream(node->host, node->port);
    if (upstream_fd < 0) {
        record_upstream_result(upstream_idx, 503);
        const char* err_502 = 
            "HTTP/1.1 502 Bad Gateway\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 35\r\n\r\n"
            "Service Mesh: Upstream connect fail\n";
        write(client_fd, err_502, strlen(err_502));
        close(client_fd);
        return;
    }

    /* Ін'єкція службового заголовка трейсингу перед завершенням заголовків \r\n\r\n */
    char modified_req[BUFFER_SIZE + 256];
    char* sep = strstr(buffer, "\r\n\r\n");
    if (sep) {
        size_t head_len = (size_t)(sep - buffer);
        snprintf(modified_req, sizeof(modified_req),
                 "%.*s\r\nx-mesh-proxied: sidecar-c-v1\r\nx-request-id: req-%lx\r\n\r\n%s",
                 (int)head_len, buffer, (unsigned long)time(NULL), sep + 4);
        write(upstream_fd, modified_req, strlen(modified_req));
    } else {
        write(upstream_fd, buffer, bytes_read);
    }

    /* Читання відповіді бекенда та передача клієнту */
    ssize_t up_read = read(upstream_fd, buffer, sizeof(buffer) - 1);
    if (up_read > 0) {
        buffer[up_read] = '\0';
        int status = parse_http_status(buffer, up_read);
        record_upstream_result(upstream_idx, status);
        write(client_fd, buffer, up_read);
    } else {
        record_upstream_result(upstream_idx, 504);
    }

    close(upstream_fd);
    close(client_fd);
}

int main(void) {
    init_upstream_pool();
    add_upstream("127.0.0.1", 8081);
    add_upstream("127.0.0.1", 8082);
    add_upstream("127.0.0.1", 8083);

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return 1;
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in address = {
        .sin_family = AF_INET,
        .sin_addr.s_addr = INADDR_ANY,
        .sin_port = htons(LISTEN_PORT)
    };

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("bind");
        close(server_fd);
        return 1;
    }

    if (listen(server_fd, 64) < 0) {
        perror("listen");
        close(server_fd);
        return 1;
    }

    printf("=== L7 Сайдкар-проксі (C) запущено на порті %d ===\n", LISTEN_PORT);

    while (1) {
        struct sockaddr_in client_addr;
        socklen_t addrlen = sizeof(client_addr);
        int client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &addrlen);
        if (client_fd >= 0) {
            handle_client(client_fd);
        }
    }

    close(server_fd);
    return 0;
}
