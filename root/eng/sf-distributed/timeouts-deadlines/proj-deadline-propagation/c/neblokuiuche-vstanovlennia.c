/* Встановлення TCP з'єднання з жорстким контролем дедлайну */
int connect_with_deadline(int sock_fd, const struct sockaddr *addr, socklen_t addrlen,
                          const deadline_context_t *ctx) {
    /* Переводимо сокет у неблокуючий режим */
    int flags = fcntl(sock_fd, F_GETFL, 0);
    fcntl(sock_fd, F_SETFL, flags | O_NONBLOCK);

    int ret = connect(sock_fd, addr, addrlen);
    if (ret == 0) {
        return 0; /* З'єднання встановлено миттєво (локальний сокет) */
    }

    if (errno != EINPROGRESS) {
        return -1; /* Миттєва помилка маршрутизації */
    }

    int64_t remain_ms = context_remaining_ms(ctx);
    if (remain_ms <= 0) {
        errno = ETIMEDOUT;
        return -1;
    }

    struct pollfd pfd;
    pfd.fd = sock_fd;
    pfd.events = POLLOUT;
    pfd.revents = 0;

    ret = poll(&pfd, 1, (int)remain_ms);
    if (ret <= 0) {
        errno = (ret == 0) ? ETIMEDOUT : errno;
        return -1;
    }

    /* Перевірка помилки сокета після готовності POLLOUT */
    int sock_err = 0;
    socklen_t err_len = sizeof(sock_err);
    if (getsockopt(sock_fd, SOL_SOCKET, SO_ERROR, &sock_err, &err_len) < 0 || sock_err != 0) {
        errno = (sock_err != 0) ? sock_err : ECOMM;
        return -1;
    }

    return 0; /* TCP-з'єднання успішно встановлено в межах бюджету */
}
