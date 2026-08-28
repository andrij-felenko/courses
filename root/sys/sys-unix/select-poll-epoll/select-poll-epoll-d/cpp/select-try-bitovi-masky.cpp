fd_set rfds;
struct timeval tv;

for (;;) {
    FD_ZERO(&rfds);
    int maxfd = 0;
    for (const auto& c : conn) {
        FD_SET(c.fd, &rfds);
        maxfd = std::max(maxfd, c.fd);
    }
    tv.tv_sec = 1; tv.tv_usec = 0;

    int n = select(maxfd + 1, &rfds, nullptr, nullptr, &tv);
    if (n < 0) {
        if (errno == EINTR) continue;
        throw std::system_error(errno, std::generic_category(), "select");
    }

    for (auto& c : conn) {
        if (FD_ISSET(c.fd, &rfds)) {
            handle(c);
        }
    }
}
