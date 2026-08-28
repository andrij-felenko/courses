static int send_line(std::string_view s) {
    std::string buf(s);
    buf.push_back('\n');
    size_t off = 0;
    while (off < buf.size()) {
        ssize_t n = ::write(ctl, buf.data() + off, buf.size() - off);
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        off += static_cast<size_t>(n);
    }
    return 0;
}

static int recv_line(std::string& out) {
    out.clear();
    for (;;) {
        char c;
        ssize_t n = ::read(ctl, &c, 1);
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        if (n == 0) return -1;
        if (c == '\n') return 0;
        out.push_back(c);
    }
}

static int tcp_accept(std::string_view port) {
    struct addrinfo hints{}, *res = nullptr;
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;
    if (::getaddrinfo(nullptr, port.data(), &hints, &res) != 0) return -1;

    int srv = ::socket(res->ai_family, res->ai_socktype, 0);
    int cli = -1, on = 1;
    if (srv >= 0) {
        ::setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));
        if (::bind(srv, res->ai_addr, res->ai_addrlen) == 0 && ::listen(srv, 1) == 0)
            cli = ::accept(srv, nullptr, nullptr);
        ::close(srv);
    }
    ::freeaddrinfo(res);
    if (cli >= 0) ::setsockopt(cli, IPPROTO_TCP, TCP_NODELAY, &on, sizeof(on));
    return cli;
}

static int tcp_connect(std::string_view host, std::string_view port) {
    struct addrinfo hints{}, *res = nullptr;
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    if (::getaddrinfo(host.data(), port.data(), &hints, &res) != 0) return -1;

    int s = -1, on = 1;
    for (auto ai = res; ai; ai = ai->ai_next) {
        s = ::socket(ai->ai_family, ai->ai_socktype, 0);
        if (s < 0) continue;
        if (::connect(s, ai->ai_addr, ai->ai_addrlen) == 0) break;
        ::close(s);
        s = -1;
    }
    ::freeaddrinfo(res);
    if (s >= 0) ::setsockopt(s, IPPROTO_TCP, TCP_NODELAY, &on, sizeof(on));
    return s;
}
