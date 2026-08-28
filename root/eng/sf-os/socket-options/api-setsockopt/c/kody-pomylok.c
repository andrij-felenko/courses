/* «спробувати поставити»: відсутність опції — не привід зупинятися */
static int try_setopt(int fd, int level, int name,
                      const void *val, socklen_t len, const char *label)
{
    if (setsockopt(fd, level, name, val, len) == 0)
        return 0;
    if (errno == ENOPROTOOPT) {
        fprintf(stderr, "%s: стек не підтримує — пропущено\n", label);
        return 0;
    }
    fprintf(stderr, "%s: setsockopt: %s\n", label, strerror(errno));
    return -1;
}
