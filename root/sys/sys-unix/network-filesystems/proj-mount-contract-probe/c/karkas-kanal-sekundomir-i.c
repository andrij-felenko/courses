static int send_line(const char *s)
{
    char   buf[2048];
    size_t len = strlen(s), off = 0;

    if (len + 1 > sizeof buf) return -1;
    memcpy(buf, s, len);
    buf[len++] = '\n';
    while (off < len) {
        ssize_t n = write(ctl, buf + off, len - off);
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        off += (size_t) n;
    }
    return 0;
}

static int recv_line(char *out, size_t cap)
{
    size_t i = 0;
    for (;;) {
        char    c;
        ssize_t n = read(ctl, &c, 1);
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        if (n == 0) return -1;                       /* другий бік пішов */
        if (c == '\n') { out[i] = '\0'; return 0; }
        if (i + 1 < cap) out[i++] = c;
    }
}

static int tcp_accept(const char *port)
{
    struct addrinfo hints, *res = NULL;
    int srv = -1, cli = -1, on = 1;

    memset(&hints, 0, sizeof hints);
    hints.ai_family   = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags    = AI_PASSIVE;
    if (getaddrinfo(NULL, port, &hints, &res) != 0) return -1;

    srv = socket(res->ai_family, res->ai_socktype, 0);
    if (srv >= 0) {
        setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);
        if (bind(srv, res->ai_addr, res->ai_addrlen) == 0 && listen(srv, 1) == 0)
            cli = accept(srv, NULL, NULL);
        close(srv);
    }
    freeaddrinfo(res);
    /* без TCP_NODELAY алгоритм Нейгла міг би підмішати в наші відліки
       десятки мілісекунд затримки, яких у файловій системі немає  */
    if (cli >= 0) setsockopt(cli, IPPROTO_TCP, TCP_NODELAY, &on, sizeof on);
    return cli;
}

static int tcp_connect(const char *host, const char *port)
{
    struct addrinfo hints, *res = NULL, *ai;
    int s = -1, on = 1;

    memset(&hints, 0, sizeof hints);
    hints.ai_family   = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo(host, port, &hints, &res) != 0) return -1;

    for (ai = res; ai; ai = ai->ai_next) {
        s = socket(ai->ai_family, ai->ai_socktype, 0);
        if (s < 0) continue;
        if (connect(s, ai->ai_addr, ai->ai_addrlen) == 0) break;
        close(s);
        s = -1;
    }
    freeaddrinfo(res);
    if (s >= 0) setsockopt(s, IPPROTO_TCP, TCP_NODELAY, &on, sizeof on);
    return s;
}
