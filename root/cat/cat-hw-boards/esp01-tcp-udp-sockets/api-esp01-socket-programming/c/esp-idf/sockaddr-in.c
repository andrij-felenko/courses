#include "lwip/sockets.h"
#include "lwip/netdb.h"

void run_native_tcp_server(void *pvParameters) {
    struct sockaddr_in server_addr;
    int listen_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(80);

    bind(listen_fd, (struct sockaddr *)&server_addr, sizeof(server_addr));
    listen(listen_fd, 5);

    while (1) {
        struct sockaddr_in client_addr;
        socklen_t addr_len = sizeof(client_addr);
        int client_fd = accept(listen_fd, (struct sockaddr *)&client_addr, &addr_len);
        if (client_fd >= 0) {
            char rx_buffer[128];
            int len = recv(client_fd, rx_buffer, sizeof(rx_buffer) - 1, 0);
            if (len > 0) {
                send(client_fd, "OK", 2, 0);
            }
            close(client_fd);
        }
    }
}
