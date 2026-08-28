/* Перевірка закриття з'єднання клієнтом */
bool is_client_disconnected(int sock_fd) noexcept {
    struct pollfd pfd{sock_fd, POLLIN | POLLHUP, 0};
    const int ret = ::poll(&pfd, 1, 0);
    if (ret > 0) {
        if (pfd.revents & (POLLHUP | POLLERR | POLLNVAL)) {
            return true;
        }
        if (pfd.revents & POLLIN) {
            char peek_byte = 0;
            const ssize_t n = ::recv(sock_fd, &peek_byte, 1, MSG_PEEK | MSG_DONTWAIT);
            if (n == 0) {
                return true;
            }
        }
    }
    return false;
}
