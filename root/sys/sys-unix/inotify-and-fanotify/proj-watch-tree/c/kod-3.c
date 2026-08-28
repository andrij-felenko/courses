static void die_enospc(const struct ctx *c);

static void scan(struct ctx *c, size_t len, int parent, const char *base)
{
    int wd = inotify_add_watch(c->ifd, c->buf, WATCH_MASK);
    if (wd < 0) {
        if (errno == ENOSPC) die_enospc(c);
        if (errno != ENOENT && errno != EACCES && errno != ENOTDIR)
            fprintf(stderr, "watchtree: %s: %s\n", c->buf, strerror(errno));
        return;                                /* зник або не наш — просто не покриваємо */
    }
    if (map_get(wd)) return;                   /* цей inode уже в карті: гілку покрито */
    map_add(wd, parent, base);

    DIR *d = opendir(c->buf);                  /* перечитуємо ПІСЛЯ того, як стеження стоїть */
    if (!d) {
        if (errno != ENOENT && errno != EACCES)
            fprintf(stderr, "watchtree: %s: %s\n", c->buf, strerror(errno));
        return;
    }
    for (struct dirent *e; (e = readdir(d)) != NULL; ) {
        if (e->d_name[0] == '.' && (e->d_name[1] == '\0' ||
            (e->d_name[1] == '.' && e->d_name[2] == '\0')))
            continue;

        int isdir;
        if (e->d_type == DT_DIR)          isdir = 1;
        else if (e->d_type != DT_UNKNOWN) isdir = 0;
        else {                                 /* ФС не заповнила d_type — питаємо окремо */
            struct stat st;
            isdir = fstatat(dirfd(d), e->d_name, &st, AT_SYMLINK_NOFOLLOW) == 0
                    && S_ISDIR(st.st_mode);
        }

        printf("= %s/%s\n", c->buf, e->d_name);
        if (!isdir) continue;

        size_t nl = strlen(e->d_name);
        if (len + 1 + nl >= PATH_MAX) continue;
        c->buf[len] = '/';
        memcpy(c->buf + len + 1, e->d_name, nl + 1);
        scan(c, len + 1 + nl, wd, e->d_name);
        c->buf[len] = '\0';                    /* відкотили — знову шлях батька */
    }
    closedir(d);
}
