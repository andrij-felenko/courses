// RAII-обгортка гарантує закриття дескриптора навіть у разі винятку
class scoped_fd {
    int fd_{-1};
public:
    explicit scoped_fd(int fd) : fd_(fd) {}
    ~scoped_fd() { if (fd_ >= 0) ::close(fd_); }
    scoped_fd(const scoped_fd&) = delete;
    scoped_fd& operator=(const scoped_fd&) = delete;
    scoped_fd(scoped_fd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    int get() const { return fd_; }
    explicit operator bool() const { return fd_ >= 0; }
};

scoped_fd fd{::open("/var/tmp", O_TMPFILE | O_RDWR, 0600)};
if (!fd) {
    throw std::system_error(errno, std::generic_category(), "open O_TMPFILE failed");
}
// Об'єкт живе тільки на дескрипторі; на виході з області видимості scoped_fd закриє fd, і ядро вивільнить inode
::write(fd.get(), buf, n);
