#include "lwip/sockets.h"

void native_udp_task(void *pvParameters) {
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    struct sockaddr_in rx_addr;
    rx_addr.sin_family = AF_INET;
    rx_addr.sin_port = htons(4210);
    rx_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    
    bind(sock, (struct sockaddr *)&rx_addr, sizeof(rx_addr));

    char rx_buffer[128];
    struct sockaddr_in src_addr;
    socklen_t addr_len = sizeof(src_addr);

    while (1) {
        int len = recvfrom(sock, rx_buffer, sizeof(rx_buffer) - 1, 0, (struct sockaddr *)&src_addr, &addr_len);
        if (len > 0) {
            sendto(sock, "ACK", 3, 0, (struct sockaddr *)&src_addr, addr_len);
        }
    }
}
