void safe_format_error(int errnum, char *out_buf, size_t buflen) {
    if (buflen == 0) return;
    out_buf[0] = '\0';

#if defined(_GNU_SOURCE) && !defined(__APPLE__) && !defined(__FreeBSD__)
    /* GNU версія повертає вказівник */
    char *res = strerror_r(errnum, out_buf, buflen);
    if (res != out_buf) {
        strncpy(out_buf, res, buflen - 1);
        out_buf[buflen - 1] = '\0';
    }
#else
    /* POSIX XSI версія повертає int */
    if (strerror_r(errnum, out_buf, buflen) != 0) {
        snprintf(out_buf, buflen, "Unknown error %d", errnum);
    }
#endif
}
