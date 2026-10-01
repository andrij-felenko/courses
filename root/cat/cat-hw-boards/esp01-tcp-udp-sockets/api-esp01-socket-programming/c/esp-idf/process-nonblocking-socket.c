#include "lwip/sockets.h"
#include "lwip/err.h"

void process_nonblocking_socket(int sock_fd) {
    int flags = fcntl(sock_fd, F_GETFL, 0);
    // Встановлення прапорця O_NONBLOCK для неблокуючого режиму
    fcntl(sock_fd, F_SETFL, flags | O_NONBLOCK);
    
    char rx_buf[128];
    int len = recv(sock_fd, rx_buf, sizeof(rx_buf) - 1, 0);
    if (len < 0) {
        if (errno == EWOULDBLOCK || errno == EAGAIN) {
            /* Дані ще не надійшли, продовжуємо цикл */
        } else {
            /* Виникла помилка мережі, закриваємо сокет */
            close(sock_fd);
        }
    }
}
