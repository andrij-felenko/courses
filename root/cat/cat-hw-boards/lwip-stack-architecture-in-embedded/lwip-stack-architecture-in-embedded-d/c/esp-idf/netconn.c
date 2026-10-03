#include "lwip/api.h"
#include "lwip/sockets.h"

// Приклад 1: Послідовний сервер на Netconn API
void netconn_server_task(void *pvParameters) {
    struct netconn *conn = netconn_new(NETCONN_TCP);
    struct netconn *newconn;
    
    netconn_bind(conn, IP_ADDR_ANY, 8080);
    netconn_listen(conn);
    
    while (netconn_accept(conn, &newconn) == ERR_OK) {
        struct netbuf *buf;
        void *data;
        u16_t len;
        
        while (netconn_recv(newconn, &buf) == ERR_OK) {
            netbuf_data(buf, &data, &len);
            netconn_write(newconn, data, len, NETCONN_COPY);
            netbuf_delete(buf);
        }
        netconn_close(newconn);
        netconn_delete(newconn);
    }
}

// Приклад 2: Сумісний сервер на BSD Sockets API
void socket_server_task(void *pvParameters) {
    int listen_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    struct sockaddr_in dest_addr = {
        .sin_family = AF_INET,
        .sin_port = htons(8080),
        .sin_addr.s_addr = htonl(INADDR_ANY)
    };
    
    bind(listen_sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    listen(listen_sock, 1);
    
    while (1) {
        struct sockaddr_in source_addr;
        socklen_t addr_len = sizeof(source_addr);
        int sock = accept(listen_sock, (struct sockaddr *)&source_addr, &addr_len);
        if (sock >= 0) {
            char rx_buffer[128];
            int len = recv(sock, rx_buffer, sizeof(rx_buffer), 0);
            if (len > 0) {
                send(sock, rx_buffer, len, 0);
            }
            shutdown(sock, 0);
            close(sock);
        }
    }
}
