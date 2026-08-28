#include <fstream>

static long read_long(const std::string& path) {
    long v = -1;
    std::ifstream f(path);
    if (f >> v) return v;
    return -1;
}

static void die_enospc(const Context& c) {
    long lim = read_long("/proc/sys/fs/inotify/max_user_watches");
    std::cerr << "watchtree: вичерпано ліміт стежень inotify — покриття було б неповним.\n"
              << "  поставлено:          " << nwatch << " стежень\n"
              << "  межа на користувача: " << lim << "\n"
              << "  дерево:              " << c.root << "\n";
    std::exit(1);
}

static void start_group(Context& c) {
    if (c.ifd >= 0) {
        close(c.ifd);
        node_map.clear();
        moves.assign(MOVE_SLOTS, PendingMove{});
        nwatch = 0;
        todo_queue.clear();
    }
    c.ifd = inotify_init1(IN_NONBLOCK | IN_CLOEXEC);
    if (c.ifd < 0) { std::perror("inotify_init1"); std::exit(1); }

    struct epoll_event ev{.events = EPOLLIN, .data = {.fd = c.ifd}};
    if (epoll_ctl(c.ep, EPOLL_CTL_ADD, c.ifd, &ev) < 0) { std::perror("epoll_ctl"); std::exit(1); }

    c.rebuild = false;
    std::cout << "RESYNC\n";
    std::snprintf(c.buf.data(), PATH_MAX, "%s", c.root.c_str());
    scan(c, c.root.size(), -1, c.root);
    std::cout << "READY " << nwatch << "\n" << std::flush;
}

int main(int argc, char** argv) {
    if (argc != 2) { std::cerr << "вжиток: watchtree <каталог>\n"; return 2; }

    char root[PATH_MAX];
    if (!realpath(argv[1], root)) { std::perror(argv[1]); return 1; }

    Context c;
    c.root = root;
    c.buf.resize(PATH_MAX);
    c.ep = epoll_create1(EPOLL_CLOEXEC);
    if (c.ep < 0) { std::perror("epoll_create1"); return 1; }

    start_group(c);

    for (;;) {
        struct epoll_event ev[8];
        int nfd = epoll_wait(c.ep, ev, 8, next_timeout());
        if (nfd < 0) {
            if (errno == EINTR) continue;
            std::perror("epoll_wait");
            return 1;
        }
        for (int i = 0; i < nfd; i++) {
            if (ev[i].data.fd == c.ifd) drain(c);
        }

        run_todo(c);
        expire_moves(c);
        std::cout << std::flush;

        if (c.rebuild) start_group(c);
    }
}
