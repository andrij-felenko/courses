static int send_req(int sock, const struct req *rq)
{
    ssize_t n;
    do { n = send(sock, rq, sizeof *rq, MSG_NOSIGNAL); } while (n < 0 && errno == EINTR);
    return n == (ssize_t)sizeof *rq ? 0 : -1;
}

static void worker(int sock)
{
    /* Тут живе весь розбір мережевого протоколу — тисячі рядків ворожого вводу.
       Нижче лише те, як ця частина розмовляє з монітором. */
    struct req rq = { .op = OP_AUTH, .user_len = 5, .pw_len = 6 };
    memcpy(rq.user, "alice", 5);
    memcpy(rq.pw, "secret", 6);

    struct resp rs;
    int fd = -1;
    if (send_req(sock, &rq) != 0) return;
    if (recv_resp(sock, &rs, &fd) != 0 || rs.status != 0) return;

    struct req q2 = { .op = OP_LOGFD };
    if (send_req(sock, &q2) != 0) return;
    if (recv_resp(sock, &rs, &fd) != 0 || rs.status != 0 || fd < 0) return;

    /* fd — уже відкритий журнал. Його імені робітник не знає й не дізнається. */
    (void)write(fd, "session started\n", 16);
    close(fd);
}
