static void on_event(struct ctx *c, const struct inotify_event *e)
{
    if (e->mask & IN_Q_OVERFLOW) { c->rebuild = 1; return; }   /* wd тут -1 */

    struct node *n = map_get(e->wd);
    if (!n) return;                              /* подія зі знятого стеження */

    if (e->mask & IN_IGNORED)    { forget(n); return; }
    if (e->mask & IN_MOVE_SELF)  { if (n->parent < 0) c->rebuild = 1; return; }
    if (e->mask & IN_DELETE_SELF) return;        /* слідом прийде IN_IGNORED */

    if (!e->len) return;                         /* далі потрібне ім'я запису */
    int isdir = (e->mask & IN_ISDIR) != 0;

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

static void drain(struct ctx *c)
{
    static char buf[64 * 1024]
        __attribute__((aligned(__alignof__(struct inotify_event))));

    for (;;) {
        ssize_t n = read(c->ifd, buf, sizeof buf);
        if (n < 0) {
            if (errno == EINTR)  continue;
            if (errno == EAGAIN) return;         /* черга порожня — батч скінчився */
            perror("read");
            exit(1);
        }
        for (char *p = buf; p < buf + n; ) {
            const struct inotify_event *e = (const struct inotify_event *) p;
            p += sizeof *e + e->len;             /* len — поле name з доповненням, не strlen */
            on_event(c, e);
        }
    }
}
