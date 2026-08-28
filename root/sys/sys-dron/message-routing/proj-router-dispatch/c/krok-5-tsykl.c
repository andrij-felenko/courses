int main(void)
{
    struct channel ch[] = {
        { .fd = open_serial("/dev/ttyAMA0", 921600), .name = "автопілот" },
        { .fd = open_udp("0.0.0.0", 14550),          .name = "станція"   },
        { .fd = open_tcp(5760),                      .name = "логер"     },
    };
    const int n = (int)(sizeof(ch) / sizeof(ch[0]));

    for (;;) {
        struct pollfd pfd[3];
        for (int i = 0; i < n; i++) {
            pfd[i] = (struct pollfd){ .fd = ch[i].fd, .events = POLLIN };
        }
        if (poll(pfd, n, 100) <= 0) {
            continue;
        }
        const uint32_t now = now_ms();

        for (int i = 0; i < n; i++) {
            if (!(pfd[i].revents & POLLIN)) {
                continue;
            }
            struct channel *c = &ch[i];

            ssize_t got = read(c->fd, c->rx + c->rx_len, sizeof(c->rx) - c->rx_len);
            if (got <= 0) {
                continue;
            }
            c->rx_len += (size_t)got;

            for (;;) {
                struct frame f;
                bool ok;
                size_t used = frame_scan(c->rx, c->rx_len, &f, &ok);
                if (ok) {
                    chan_learn(c, f.src_sys, f.src_comp, now);
                    route(&f, c, ch, n, now);
                }
                if (used == 0) {
                    break;                    /* треба дочитати           */
                }
                c->rx_len -= used;
                memmove(c->rx, c->rx + used, c->rx_len);
                if (!ok) {
                    break;
                }
            }
        }
    }
}
