std::vector<struct pollfd> pfd;
pfd.reserve(conn.size());
for (const auto& c : conn) {
    pfd.push_back({.fd = c.fd, .events = POLLIN, .revents = 0});
}

for (;;) {
    int n = poll(pfd.data(), static_cast<nfds_t>(pfd.size()), 1000);
    if (n < 0) {
        if (errno == EINTR) continue;
        throw std::system_error(errno, std::generic_category(), "poll");
    }

    for (size_t i = 0; i < pfd.size() && n > 0; ++i) {
        if (!pfd[i].revents) continue;
        --n;
        handle(conn[i], pfd[i].revents);
    }
}
