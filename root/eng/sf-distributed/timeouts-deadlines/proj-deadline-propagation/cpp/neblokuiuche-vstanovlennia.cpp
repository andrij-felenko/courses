/* Неблокуючий connect із дедлайном на C++ */
bool connect_with_deadline(int sock_fd, const struct sockaddr* addr, socklen_t addrlen,
                           const DeadlineContext& ctx) {
    const int flags = ::fcntl(sock_fd, F_GETFL, 0);
    ::fcntl(sock_fd, F_SETFL, flags | O_NONBLOCK);

    if (::connect(sock_fd, addr, addrlen) == 0) {
        return true;
    }

    if (errno != EINPROGRESS) {
        return false;
    }

    const auto remain = ctx.remaining();
    if (remain <= std::chrono::milliseconds::zero()) {
        return false;
    }

    struct pollfd pfd{sock_fd, POLLOUT, 0};
    const int timeout_ms = static_cast<int>(remain.count());
    const int ret = ::poll(&pfd, 1, timeout_ms);

    if (ret <= 0) {
        return false;
    }

    int sock_err = 0;
    socklen_t err_len = sizeof(sock_err);
    if (::getsockopt(sock_fd, SOL_SOCKET, ERROR_PARAM, &sock_err, &err_len) < 0 || sock_err != 0) {
        return false;
    }

    return true;
}
