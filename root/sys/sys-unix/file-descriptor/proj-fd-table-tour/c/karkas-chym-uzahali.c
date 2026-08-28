/* Режим доступу зашитий у молодші біти прапорців опису. */
static const char *access_mode(int fl)
{
    switch (fl & O_ACCMODE) {
    case O_RDONLY: return "r-";
    case O_WRONLY: return "-w";
    case O_RDWR:   return "rw";
    default:       return "??";
    }
}

/* Один рядок про один номер: куди веде і які прапорці на якому рівні. */
static void show_fd(int fd)
{
    char path[64];
    char target[512];

    snprintf(path, sizeof path, "/proc/self/fd/%d", fd);
    ssize_t len = readlink(path, target, sizeof target - 1);
    if (len < 0) len = 0;          /* номер міг зникнути між двома проходами */
    target[len] = '\0';

    int fdfl = fcntl(fd, F_GETFD); /* рівень ДЕСКРИПТОРА: лише FD_CLOEXEC */
    int flfl = fcntl(fd, F_GETFL); /* рівень ОПИСУ: режим і статусні прапорці */
    if (fdfl < 0 || flfl < 0) {
        printf("  %3d  (уже закритий)\n", fd);
        return;
    }

    printf("  %3d  %-28s  %s%s%s%s\n",
           fd, target[0] ? target : "?",
           access_mode(flfl),
           (flfl & O_APPEND)    ? " O_APPEND"    : "",
           (flfl & O_NONBLOCK)  ? " O_NONBLOCK"  : "",
           (fdfl & FD_CLOEXEC)  ? " +FD_CLOEXEC" : "");
}

/* Скільки номерів зайнято просто зараз (-1, якщо подивитися нічим). */
static int count_fds(void)
{
    int fds[1024];
    return list_fds(fds, 1024);
}

static void dump_fds(const char *label)
{
    int fds[1024];
    int n = list_fds(fds, 1024);
    if (n < 0) {
        printf("%s — подивитися нічим: %s\n", label, strerror(errno));
        return;
    }
    printf("%s — записів: %d\n", label, n);
    for (int i = 0; i < n; i++)
        show_fd(fds[i]);
}

/* Друкує невеликий файл із відступом — щоб одразу бачити результат досліду. */
static void show_file(const char *path)
{
    int fd = open(path, O_RDONLY);
    if (fd < 0) die("open для читання");

    char buf[1024];
    ssize_t n;
    int at_line_start = 1;
    while ((n = read(fd, buf, sizeof buf)) > 0) {
        for (ssize_t i = 0; i < n; i++) {
            if (at_line_start) { fputs("  | ", stdout); at_line_start = 0; }
            putchar(buf[i]);
            if (buf[i] == '\n') at_line_start = 1;
        }
    }
    if (n < 0) die("read");
    if (close(fd) < 0) die("close");
}
