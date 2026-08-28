#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define API_BACKEND_PORT 8081
#define STATIC_BACKEND_PORT 8082

static int connect_backend(int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    if (connect(fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

/* L7 розбір HTTP-запиту та маршрутизація за префіксом шляху */
void l7_handle_http_request(int client_fd, const char* client_ip) {
    char req_buf[8192];
    ssize_t bytes_read = read(client_fd, req_buf, sizeof(req_buf) - 1);
    if (bytes_read <= 0) {
        close(client_fd);
        return;
    }
    req_buf[bytes_read] = '\0';

    char method[16], path[256], proto[16];
    if (sscanf(req_buf, "%15s %255s %15s", method, path, proto) != 3) {
        const char* bad_req = "HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n";
        write(client_fd, bad_req, strlen(bad_req));
        close(client_fd);
        return;
    }

    /* Семантичне рішення L7: вибір цільового бекенда за URI */
    int target_port = (strncmp(path, "/api", 4) == 0) ? API_BACKEND_PORT : STATIC_BACKEND_PORT;
    int backend_fd = connect_backend(target_port);
    if (backend_fd < 0) {
        const char* err_503 = "HTTP/1.1 503 Service Unavailable\r\nContent-Length: 0\r\n\r\n";
        write(client_fd, err_503, strlen(err_503));
        close(client_fd);
        return;
    }

    /* Модифікація заголовків: додавання X-Forwarded-For */
    char forward_header[128];
    snprintf(forward_header, sizeof(forward_header), "X-Forwarded-For: %s\r\n", client_ip);

    /* Знаходимо кінець рядка запиту та вставляємо заголовок */
    char* header_insert_pt = strstr(req_buf, "\r\n");
    if (header_insert_pt) {
        header_insert_pt += 2;
        write(backend_fd, req_buf, header_insert_pt - req_buf);
        write(backend_fd, forward_header, strlen(forward_header));
        write(backend_fd, header_insert_pt, strlen(header_insert_pt));
    } else {
        write(backend_fd, req_buf, bytes_read);
    }

    /* Читання відповіді бекенда та повернення клієнту */
    char res_buf[8192];
    ssize_t n;
    while ((n = read(backend_fd, res_buf, sizeof(res_buf))) > 0) {
        write(client_fd, res_buf, n);
    }

    close(backend_fd);
    close(client_fd);
}
