/* Утримати обхід усередині root_fd — власними руками. */
static int walk_beneath(int root_fd, const char *path)
{
    struct stat root_st;
    if (fstatat(root_fd, "", &root_st, AT_EMPTY_PATH) < 0) return -1;

    int dir = dup(root_fd);
    if (dir < 0) return -1;
    int depth = 0;                 /* скільки складників углиб від кореня */

    char buf[PATH_MAX];
    if (strlen(path) >= sizeof buf) { errno = ENAMETOOLONG; goto fail; }
    strcpy(buf, path);
    char *rest = buf;

    for (;;) {
        while (*rest == '/') rest++;
        if (*rest == '\0') return dir;

        char  *slash = strchr(rest, '/');
        size_t len   = slash ? (size_t)(slash - rest) : strlen(rest);
        char   comp[NAME_MAX + 1];

        if (len > NAME_MAX) { errno = ENAMETOOLONG; goto fail; }
        memcpy(comp, rest, len);
        comp[len] = '\0';
        rest = slash ? slash + 1 : rest + len;

        if (strcmp(comp, ".") == 0) continue;

        if (strcmp(comp, "..") == 0) {
            if (depth == 0) { errno = EXDEV; goto fail; }   /* уперлися в корінь */
            int up = openat(dir, "..", O_PATH | O_CLOEXEC);
            if (up < 0) goto fail;
            close(dir);
            dir = up;
            depth--;
            continue;
        }

        int next = openat(dir, comp, O_PATH | O_NOFOLLOW | O_CLOEXEC);
        if (next < 0) goto fail;

        struct stat st;
        if (fstatat(next, "", &st, AT_EMPTY_PATH) < 0) { close(next); goto fail; }
        if (S_ISLNK(st.st_mode))         { close(next); errno = ELOOP; goto fail; }
        if (st.st_dev != root_st.st_dev) { close(next); errno = EXDEV; goto fail; }

        close(dir);
        dir = next;
        depth++;
    }

fail:
    { int e = errno; if (dir >= 0) close(dir); errno = e; }
    return -1;
}
