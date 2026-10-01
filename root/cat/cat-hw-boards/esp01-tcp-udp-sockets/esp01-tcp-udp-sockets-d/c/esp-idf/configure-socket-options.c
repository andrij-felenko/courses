#include "lwip/sockets.h"

int socket_fd;
uint8_t telemetry_buffer[512];
size_t buffer_index = 0;

void configure_socket_options(int fd) {
    int nodelay_flag = 1;
    // Вимикаємо затримку Nagle algorithm на рівні сокета lwIP
    setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &nodelay_flag, sizeof(nodelay_flag));
}

void send_aggregated_sample(uint8_t sample) {
    telemetry_buffer[buffer_index++] = sample;
    if (buffer_index >= sizeof(telemetry_buffer)) {
        send(socket_fd, telemetry_buffer, buffer_index, 0);
        buffer_index = 0;
    }
}
