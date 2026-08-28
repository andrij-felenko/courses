static void drain_messages(int fd)
{
    char buf[4096];
    ssize_t n;
    while ((n = read(fd, buf, sizeof buf - 1)) > 0) {
        buf[n] = '\0';
        /* приклад справжнього рядка: "einvalid option 'nosuchopt'" */
        fprintf(stderr, "%s: %s\n",
                buf[0] == 'e' ? "помилка" :
                buf[0] == 'w' ? "увага"   : "довідка", buf + 1);
    }
}
