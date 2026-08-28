/* значення атрибута в щойно виділеній пам'яті; NULL і errno при відмові */
static void *xattr_dup(const char *path, const char *name, ssize_t *out_len)
{
    for (int tries = 0; tries < 8; tries++) {
        ssize_t need = getxattr(path, name, NULL, 0);   /* лише розмір */
        if (need < 0)
            return NULL;                                /* ENODATA, ENOTSUP … */

        char *buf = malloc((size_t)need ? (size_t)need : 1);
        if (!buf)
            return NULL;

        ssize_t got = getxattr(path, name, buf, (size_t)need);
        if (got >= 0) {
            *out_len = got;
            return buf;
        }
        free(buf);
        if (errno != ERANGE)                            /* не гонка — здаємося */
            return NULL;
    }                                                   /* хтось активно пише — пробуємо ще */
    errno = ERANGE;
    return NULL;
}
