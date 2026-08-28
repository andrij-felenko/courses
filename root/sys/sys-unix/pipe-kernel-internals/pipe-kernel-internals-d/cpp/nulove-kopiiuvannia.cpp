#include <fcntl.h>
#include <unistd.h>
#include <system_error>
#include <memory>

class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) ::close(fd_);
        fd_ = new_fd;
    }

private:
    int fd_;
};

ssize_t zero_copy_stream(int sock_fd, int file_fd, size_t total_bytes) {
    int pfd[2];
    if (::pipe(pfd) < 0) {
        throw std::system_error(errno, std::generic_category(), "pipe");
    }
    UniqueFd read_end(pfd[0]);
    UniqueFd write_end(pfd[1]);

    size_t transferred = 0;
    while (transferred < total_bytes) {
        ssize_t n_in = ::splice(sock_fd, nullptr, write_end.get(), nullptr,
                                total_bytes - transferred, SPLICE_F_MOVE | SPLICE_F_MORE);
        if (n_in <= 0) break;

        ssize_t n_out = ::splice(read_end.get(), nullptr, file_fd, nullptr,
                                 static_cast<size_t>(n_in), SPLICE_F_MOVE | SPLICE_F_MORE);
        if (n_out <= 0) break;

        transferred += static_cast<size_t>(n_out);
    }

    return static_cast<ssize_t>(transferred);
}
