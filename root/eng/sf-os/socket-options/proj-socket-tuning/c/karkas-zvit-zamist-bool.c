static int set_tv(int fd, int name, long ms, const char *label, sock_report *rep)
{
    opt_result *o = slot(rep, label);
    o->want = ms;

    /* Це ЄДИНЕ місце модуля, що знає про struct timeval: у Windows та сама
       опція бере просто число мілісекунд, тож портується один рядок. */
    struct timeval tv = { .tv_sec = ms / 1000, .tv_usec = (ms % 1000) * 1000 };
    if (setsockopt(fd, SOL_SOCKET, name, &tv, sizeof tv) < 0) {
        o->err = errno;
        o->state = (errno == ENOPROTOOPT) ? OPT_UNSUPPORTED : OPT_FAILED;
        if (o->state == OPT_UNSUPPORTED) { rep->unsupported++; return 0; }
        rep->failed++;
        return 1;
    }

    struct timeval back;
    socklen_t len = sizeof back;
    if (getsockopt(fd, SOL_SOCKET, name, &back, &len) < 0) {
        o->err = errno; o->state = OPT_FAILED; rep->failed++; return 1;
    }
    o->got = back.tv_sec * 1000L + back.tv_usec / 1000;
    if (o->got != o->want) { o->state = OPT_CHANGED; rep->changed++; }
    return 0;
}
