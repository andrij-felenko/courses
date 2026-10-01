#include "lwip/sockets.h"

void send_udp_telemetry(const char *ip_str, uint16_t port, const uint8_t *data, size_t len) {
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) return;

    struct sockaddr_in dest_addr;
    dest_addr.sin_addr.s_addr = inet_addr(ip_str);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(port);

    // Відправка датаграми без попереднього рукостискання
    sendto(sock, data, len, 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    close(sock);
}
