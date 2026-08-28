UniqueFd open_file(const char* path, int flags) {
    UniqueFd fd(FdHandle{::open(path, flags)});
    if (!fd) throw std::system_error(errno, std::system_category(), path);
    return fd;
}

inline int native(const UniqueFd& f) noexcept { return f.get().fd(); }

auto log = open_file("run.log", O_RDONLY);
char buf[4096];
ssize_t n = ::read(native(log), buf, sizeof buf);    // close — на будь-якому виході
