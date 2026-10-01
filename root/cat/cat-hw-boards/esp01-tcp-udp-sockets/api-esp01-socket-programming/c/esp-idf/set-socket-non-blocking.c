#include "lwip/sockets.h"
#include "lwip/sys.h"

void set_socket_non_blocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

void non_blocking_recv_example(int sock_fd) {
    set_socket_non_blocking(sock_fd);
    char buf[64];
    int res = recv(sock_fd, buf, sizeof(buf), 0);
    
    if (res < 0) {
        if (errno == EWOULDBLOCK || errno == EAGAIN) {
            // Буфер порожній, продовжуємо виконання інших задач
        } else {
            // Фатальна помилка мережі, закриваємо сокет
            close(sock_fd);
        }
    } else if (res == 0) {
        // З'єднання закрито віддаленою стороною
        close(sock_fd);
    }
}
