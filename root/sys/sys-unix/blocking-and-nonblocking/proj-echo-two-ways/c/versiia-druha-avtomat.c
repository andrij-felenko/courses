static struct conn *conn_new(int fd)
{
    struct conn *c = calloc(1, sizeof *c);
    if (c != NULL) {
        c->fd = fd;
        c->phase = PH_HEADER;
    }
    return c;
}

static void conn_close(int ep, struct conn *c)
{
    epoll_ctl(ep, EPOLL_CTL_DEL, c->fd, NULL);   /* NULL дозволено з Linux 2.6.9 */
    close(c->fd);
    free(c->body);
    free(c->out);
    free(c);
}
