static long read_long(const char *path)
{
    long v = -1;
    FILE *f = fopen(path, "r");
    if (f) {
        if (fscanf(f, "%ld", &v) != 1) v = -1;
        fclose(f);
    }
    return v;
}

static void die_enospc(const struct ctx *c)
{
    long lim = read_long("/proc/sys/fs/inotify/max_user_watches");
    fprintf(stderr,
        "watchtree: вичерпано ліміт стежень inotify — покриття було б неповним.\n"
        "  поставлено:      %zu стежень\n"
        "  межа на користувача: %ld  (/proc/sys/fs/inotify/max_user_watches)\n"
        "  дерево:          %s\n"
        "  підняти межу:    sudo sysctl -w fs.inotify.max_user_watches=%ld\n"
        "  або виключити важкі гілки: node_modules, .git, target, build\n",
        nwatch, lim, c->root, lim > 0 ? lim * 4 : 65536);
    exit(1);
}

static void start_group(struct ctx *c)
{
    if (c->ifd >= 0) {
        close(c->ifd);              /* група гине з усіма стеженнями; epoll забуде fd сам */
        for (unsigned i = 0; i < NBUCKET; i++)
            for (struct node *n = tab[i], *next; n; n = next) {
                next = n->hnext;
                free(n->name);
                free(n);
            }
        memset(tab, 0, sizeof tab);
        memset(moves, 0, sizeof moves);
        nwatch = 0;
        ntodo = 0;
    }
    c->ifd = inotify_init1(IN_NONBLOCK | IN_CLOEXEC);
    if (c->ifd < 0) { perror("inotify_init1"); exit(1); }

    struct epoll_event ev = { .events = EPOLLIN, .data.fd = c->ifd };
    if (epoll_ctl(c->ep, EPOLL_CTL_ADD, c->ifd, &ev) < 0) { perror("epoll_ctl"); exit(1); }

    c->rebuild = 0;
    printf("RESYNC\n");             /* усе, що споживач знав, — недійсне */
    snprintf(c->buf, PATH_MAX, "%s", c->root);
    scan(c, strlen(c->buf), -1, c->root);
    printf("READY %zu\n", nwatch);
    fflush(stdout);
}

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "вжиток: watchtree <каталог>\n"); return 2; }

    static char root[PATH_MAX];
    if (!realpath(argv[1], root)) { perror(argv[1]); return 1; }

    struct ctx c = { .ifd = -1, .root = root, .buf = xmalloc(PATH_MAX), .rebuild = 0 };
    c.ep = epoll_create1(EPOLL_CLOEXEC);
    if (c.ep < 0) { perror("epoll_create1"); return 1; }

    start_group(&c);

    for (;;) {
        struct epoll_event ev[8];
        int nfd = epoll_wait(c.ep, ev, 8, next_timeout());
        if (nfd < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            return 1;
        }
        for (int i = 0; i < nfd; i++)
            if (ev[i].data.fd == c.ifd) drain(&c);
        /* сюди ж лягають інші джерела: сокет керування, signalfd, timerfd */

        run_todo(&c);               /* нові стеження — лише після спорожнілої черги */
        expire_moves(&c);
        fflush(stdout);

        if (c.rebuild) start_group(&c);
    }
}
