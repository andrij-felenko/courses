int get_secure_bytes(void *buf, size_t n)
{
    uint8_t *p = buf;
    size_t got = 0;

    while (got < n) {
        ssize_t r = getrandom(p + got, n - got, 0);
        if (r > 0)  { got += (size_t)r; continue; }
        if (r == 0) { errno = EIO; goto fail; }   /* не буває, але цикл мусить кінчатися */
        if (errno == EINTR)  continue;            /* сигнал під час очікування */
        if (errno == ENOSYS || errno == EPERM) break;  /* виклику немає — далі запасним */
        goto fail;                                /* EFAULT і подібне — помилка в нас */
    }
    if (got == n)
        return 0;

    if (urandom_fd < 0) { errno = ENOSYS; goto fail; }

    while (got < n) {
        ssize_t r = read(urandom_fd, p + got, n - got);
        if (r > 0)  { got += (size_t)r; continue; }
        if (r == 0) { errno = EIO; goto fail; }   /* кінця в /dev/urandom не буває */
        if (errno == EINTR) continue;
        goto fail;
    }
    return 0;

fail: {
        int saved = errno;
        explicit_bzero(buf, n);   /* напівзаповнений буфер не сміє піти в діло */
        errno = saved;
        return -1;
    }
}
