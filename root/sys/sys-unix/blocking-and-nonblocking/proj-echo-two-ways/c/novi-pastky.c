#define OUT_HIGH  (256u * 1024u)

/* замість want_write зберігаємо всю маску */
static int arm(int ep, struct conn *c)
{
    size_t tail = c->out_len - c->out_off;
    int m = 0;
    if (tail < OUT_HIGH) m |= EPOLLIN;    /* поки черга не роздулась — читаємо */
    if (tail > 0)        m |= EPOLLOUT;   /* є хвіст — чекаємо на місце        */

    if (m == c->mask)
        return 0;

    struct epoll_event ev;
    memset(&ev, 0, sizeof ev);
    ev.events   = (uint32_t)m;
    ev.data.ptr = c;
    if (epoll_ctl(ep, EPOLL_CTL_MOD, c->fd, &ev) < 0)
        return -1;

    c->mask = m;
    return 0;
}
