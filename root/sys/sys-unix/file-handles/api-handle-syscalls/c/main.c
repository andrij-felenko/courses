/* рукоятка у свіжовиділеній пам'яті, або NULL із причиною в errno */
static struct file_handle *fh_get(int dirfd, const char *path,
                                  int *mount_id, int flags)
{
    struct file_handle probe, *fh;

    probe.handle_bytes = 0;                  /* перший виклик — питання про розмір */
    if (name_to_handle_at(dirfd, path, &probe, mount_id, flags) == 0) {
        errno = EIO;                         /* нуль байтів — такого не буває */
        return NULL;
    }
    if (errno != EOVERFLOW)
        return NULL;                         /* EOPNOTSUPP, ENOENT, EFAULT… */
    if (probe.handle_bytes == 0) {
        errno = EOPNOTSUPP;                  /* розмір не проставлено, див. нижче */
        return NULL;
    }

    fh = malloc(sizeof *fh + probe.handle_bytes);
    if (fh == NULL)
        return NULL;
    fh->handle_bytes = probe.handle_bytes;

    if (name_to_handle_at(dirfd, path, fh, mount_id, flags) < 0) {
        int saved = errno;
        free(fh);
        errno = saved;
        return NULL;
    }
    return fh;
}
