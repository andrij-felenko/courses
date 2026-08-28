static void on_event(Context& c, const struct inotify_event* e) {
    if (e->mask & IN_Q_OVERFLOW) { c.rebuild = true; return; }

    Node* n = map_get(e->wd);
    if (!n) return;

    if (e->mask & IN_IGNORED)    { forget(n); return; }
    if (e->mask & IN_MOVE_SELF)  { if (n->parent < 0) c.rebuild = true; return; }
    if (e->mask & IN_DELETE_SELF) return;

    if (!e->len) return;
    bool isdir = (e->mask & IN_ISDIR) != 0;

    if (e->mask & IN_MOVED_FROM)  { move_out(c, n, e->name, isdir, e->cookie); return; }
    if (e->mask & IN_MOVED_TO)    { move_in (c, n, e->name, isdir, e->cookie); return; }
    if (e->mask & IN_CREATE) {
        emit("+", n->wd, e->name);
        if (isdir) defer_scan(c, n->wd, e->name);
        return;
    }
    if (e->mask & IN_DELETE)      { emit("-", n->wd, e->name); return; }
    if (e->mask & IN_CLOSE_WRITE) { emit("w", n->wd, e->name); return; }
}

static void drain(Context& c) {
    alignas(struct inotify_event) static char buf[64 * 1024];
    for (;;) {
        ssize_t n = read(c.ifd, buf, sizeof(buf));
        if (n < 0) {
            if (errno == EINTR)  continue;
            if (errno == EAGAIN) return;
            std::perror("read");
            std::exit(1);
        }
        for (char* p = buf; p < buf + n; ) {
            auto* e = reinterpret_cast<const struct inotify_event*>(p);
            p += sizeof(*e) + e->len;
            on_event(c, e);
        }
    }
}
