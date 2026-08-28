class FdHandle {
    int fd_ = -1;                                    // порожнє значення — саме -1
public:
    FdHandle() = default;
    FdHandle(std::nullptr_t) noexcept {}
    explicit FdHandle(int fd) noexcept : fd_(fd) {}

    int  fd() const noexcept { return fd_; }
    explicit operator bool() const noexcept { return fd_ != -1; }

    friend bool operator==(FdHandle a, FdHandle b) noexcept { return a.fd_ == b.fd_; }
    friend bool operator==(FdHandle h, std::nullptr_t) noexcept { return h.fd_ == -1; }
};
