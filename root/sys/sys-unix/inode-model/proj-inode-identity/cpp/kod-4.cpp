// У C++ обхід реалізують із використанням RAII для DIR* та std::vector<std::string>:
struct unique_dir {
    DIR* d{nullptr};
    explicit unique_dir(DIR* dir) : d(dir) {}
    ~unique_dir() { if (d) ::closedir(d); }
    unique_dir(const unique_dir&) = delete;
    unique_dir& operator=(const unique_dir&) = delete;
    DIR* get() const { return d; }
    explicit operator bool() const { return d != nullptr; }
};

void walk(int dfd, std::string& path, context& c) {
    unique_dir dir{::fdopendir(dfd)};
    if (!dir) {
        warn_at(c, path, "fdopendir");
        ::close(dfd);
        return;
    }

    std::vector<std::string> names;
    for (;;) {
        errno = 0;
        struct dirent *e = ::readdir(dir.get());
        if (!e) {
            if (errno != 0) warn_at(c, path, "readdir");
            break;
        }
        if (e->d_name[0] == '.' && (e->d_name[1] == '\0' || 
            (e->d_name[1] == '.' && e->d_name[2] == '\0')))
            continue;
        names.emplace_back(e->d_name);
    }

    std::sort(names.begin(), names.end());
    int fd = ::dirfd(dir.get());

    for (size_t i = 0; i < names.size(); ++i) {
        if (i > 0 && names[i] == names[i - 1]) continue;

        const auto& name = names[i];
        size_t saved_len = path.length();
        if (!path.empty() && path.back() != '/') path += '/';
        path += name;

        struct stat st{};
        if (fstatat_retry(fd, name.c_str(), &st, AT_SYMLINK_NOFOLLOW) != 0) {
            if (errno == ENOENT) c.vanished++;
            else warn_at(c, path, "fstatat");
            path.resize(saved_len);
            continue;
        }

        account(c, st, path);

        if (S_ISDIR(st.st_mode)) {
            if (c.one_fs && st.st_dev != c.root_dev) {
                c.crossings++;
                path.resize(saved_len);
                continue;
            }

            int sub = openat_retry(fd, name.c_str(), O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
            if (sub < 0) { warn_at(c, path, "openat"); path.resize(saved_len); continue; }

            struct stat sst{};
            if (::fstat(sub, &sst) != 0 || sst.st_dev != st.st_dev || sst.st_ino != st.st_ino) {
                warn_at(c, path, "підмінено між stat і open");
                ::close(sub);
                path.resize(saved_len);
                continue;
            }

            walk(sub, path, c);
        }
        path.resize(saved_len);
    }
}
