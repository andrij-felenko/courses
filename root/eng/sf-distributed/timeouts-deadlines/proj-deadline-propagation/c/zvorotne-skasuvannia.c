/* Перевірка, чи не закрив клієнт сокет під час виконання запиту */
bool is_socket_peer_closed(int sock_fd) {
    struct pollfd pfd;
    pfd.fd = sock_fd;
    pfd.events = POLLIN | POLLHUP;
    pfd.revents = 0;

    int ret = poll(&pfd, 1, 0); /* Миттєвий неблокуючий замір (таймаут 0) */
    if (ret > 0) {
        if (pfd.revents & (POLLHUP | POLLERR | POLLNVAL)) {
            return true; /* Клієнт розірвав з'єднання */
        }
        /* Якщо сокет готовий до читання, перевіряємо чи це EOF (0 байтів) */
        if (pfd.revents & POLLIN) {
            char peek_buf[1];
            ssize_t n = recv(sock_fd, peek_buf, 1, MSG_PEEK | MSG_DONTWAIT);
            if (n == 0) {
                return true; /* FIN отримано від клієнта */
            }
        }
    }
    return false;
}
