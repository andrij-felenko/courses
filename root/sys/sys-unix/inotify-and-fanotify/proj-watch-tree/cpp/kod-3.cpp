static void die_enospc(const Context& c);

static void scan(Context& c, size_t len, int parent, const std::string& base) {
    int wd = inotify_add_watch(c.ifd, c.buf.data(), WATCH_MASK);
    if (wd < 0) {
        if (errno == ENOSPC) die_enospc(c);
        if (errno != ENOENT && errno != EACCES && errno != ENOTDIR)
            std::cerr << "watchtree: " << c.buf.data() << ": " << std::strerror(errno) << "\n";
        return;
    }
    if (map_get(wd)) return;
    map_add(wd, parent, base);

    DIR* d = opendir(c.buf.data());
    if (!d) {
        if (errno != ENOENT && errno != EACCES)
            std::cerr << "watchtree: " << c.buf.data() << ": " << std::strerror(errno) << "\n";
        return;
    }
    for (struct dirent* e; (e = readdir(d)) != nullptr; ) {
        if (e->d_name[0] == '.' && (e->d_name[1] == '\0' ||
            (e->d_name[1] == '.' && e->d_name[2] == '\0')))
            continue;

        bool isdir = false;
        if (e->d_type == DT_DIR)          isdir = true;
        else if (e->d_type != DT_UNKNOWN) isdir = false;
        else {
            struct stat st;
            isdir = fstatat(dirfd(d), e->d_name, &st, AT_SYMLINK_NOFOLLOW) == 0 && S_ISDIR(st.st_mode);
        }

        std::cout << "= " << c.buf.data() << "/" << e->d_name << "\n";
        if (!isdir) continue;

        size_t nl = std::strlen(e->d_name);
        if (len + 1 + nl >= PATH_MAX) continue;
        c.buf[len] = '/';
        std::memcpy(c.buf.data() + len + 1, e->d_name, nl + 1);
        scan(c, len + 1 + nl, wd, e->d_name);
        c.buf[len] = '\0';
    }
    closedir(d);
}
