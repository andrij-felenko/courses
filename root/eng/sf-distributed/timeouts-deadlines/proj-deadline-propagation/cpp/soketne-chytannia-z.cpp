/* RAII обгортка над сокетом */
class UniqueSocket {
public:
    explicit UniqueSocket(int fd) noexcept : fd_(fd) {}
    ~UniqueSocket() { if (fd_ >= 0) ::close(fd_); }
    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;
    UniqueSocket(UniqueSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    [[nodiscard]] int get() const noexcept { return fd_; }
private:
    int fd_;
};

/* Читання точної кількості байтів у межах дедлайну */
bool read_exact(int sock_fd, std::span<uint8_t> buffer, const DeadlineContext& ctx) {
    size_t offset = 0;
    while (offset < buffer.size()) {
        const auto remain = ctx.remaining();
        if (remain <= std::chrono::milliseconds::zero()) {
            return false; /* Час вичерпано */
        }

        struct pollfd pfd{sock_fd, POLLIN, 0};
        const int timeout_ms = static_cast<int>(remain.count());
        const int ret = ::poll(&pfd, 1, timeout_ms);

        if (ret < 0) {
            if (errno == EINTR) continue;
            return false;
        }
        if (ret == 0) {
            return false; /* Таймаут poll */
        }

        if (pfd.revents & (POLLERR | POLLHUP | POLLNVAL)) {
            return false;
        }

        if (pfd.revents & POLLIN) {
            const ssize_t n = ::recv(sock_fd, buffer.data() + offset,
                                     buffer.size() - offset, MSG_DONTWAIT);
            if (n < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) continue;
                return false;
            }
            if (n == 0) {
                return false; /* Обрив зв'язку */
            }
            offset += static_cast<size_t>(n);
        }
    }
    return true;
}
