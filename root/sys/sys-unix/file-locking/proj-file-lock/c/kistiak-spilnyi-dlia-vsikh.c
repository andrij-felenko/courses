/* Прочитати число, збільшити, записати назад і лишити слід
   у журналі. Усе між lock_take і lock_drop — критична ділянка.     */
static int bump_once(int fd, int logfd)
{
    char buf[32], line[64];
    unsigned long long value = 0;
    ssize_t got;
    char *end;
    int n, m, saved;

    if (lock_take(fd) != 0) return -1;

    got = pread_all(fd, buf, sizeof buf - 1, 0);
    if (got < 0) goto fail;
    buf[got] = '\0';

    if (got > 0) {                     /* порожній файл — це чесний нуль */
        errno = 0;
        value = strtoull(buf, &end, 10);
        if (errno != 0 || end == buf) { errno = EINVAL; goto fail; }
    }

    value += 1;
    n = snprintf(buf, sizeof buf, "%llu\n", value);
    if (pwrite_all(fd, buf, (size_t) n, 0) != 0) goto fail;

    /* Число могло вкоротшати (1000 → 999), і без обрізання від
       старого запису лишився б хвіст: «9990».                       */
    if (ftruncate(fd, n) != 0) goto fail;

    m = snprintf(line, sizeof line, "pid %ld -> %llu\n",
                 (long) getpid(), value);
    if (write_all(logfd, line, (size_t) m) != 0) goto fail;

    return lock_drop(fd);

fail:
    saved = errno;                     /* lock_drop має право зіпсувати errno */
    lock_drop(fd);
    errno = saved;
    return -1;
}

int main(int argc, char **argv)
{
    long times, i;
    int fd, logfd;

    if (argc != 4) {
        fprintf(stderr, "вжиток: %s <файл-лічильника> <журнал> <разів>\n",
                argv[0]);
        return 2;
    }
    times = strtol(argv[3], NULL, 10);

    /* Файл відкриваємо ОДИН раз — поза циклом і поза замком.
       Відкриття не є частиною критичної ділянки, а от дескриптор
       мусить бути тим самим від початку до кінця роботи.            */
    fd = open(argv[1], O_RDWR | O_CREAT | O_CLOEXEC, 0644);
    if (fd < 0) { perror("open counter"); return 1; }

    logfd = open(argv[2], O_WRONLY | O_CREAT | O_APPEND | O_CLOEXEC, 0644);
    if (logfd < 0) { perror("open log"); return 1; }

    for (i = 0; i < times; i++)
        if (bump_once(fd, logfd) != 0) { perror("bump"); return 1; }

    close(logfd);
    close(fd);
    return 0;
}
