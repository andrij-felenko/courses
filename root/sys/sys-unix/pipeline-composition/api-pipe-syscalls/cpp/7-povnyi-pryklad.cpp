#include <iostream>
#include <array>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

class CustomPipe {
public:
    explicit CustomPipe(std::size_t initial_buffer_size = 131072) {
        if (::pipe2(fds_.data(), O_CLOEXEC | O_NONBLOCK) == -1) {
            throw std::system_error(errno, std::generic_category(), "pipe2 failed");
        }

        long res = ::fcntl(fds_[1], F_SETPIPE_SZ, static_cast<long>(initial_buffer_size));
        if (res != -1) {
            capacity_ = static_cast<std::size_t>(res);
        } else {
            capacity_ = 65536; // За замовчуванням 64KB
        }
    }

    ~CustomPipe() {
        if (fds_[0] != -1) ::close(fds_[0]);
        if (fds_[1] != -1) ::close(fds_[1]);
    }

    CustomPipe(const CustomPipe&) = delete;
    CustomPipe& operator=(const CustomPipe&) = delete;

    CustomPipe(CustomPipe&& other) noexcept : fds_(other.fds_), capacity_(other.capacity_) {
        other.fds_ = {-1, -1};
    }

    int read_fd() const noexcept { return fds_[0]; }
    int write_fd() const noexcept { return fds_[1]; }
    std::size_t capacity() const noexcept { return capacity_; }

private:
    std::array<int, 2> fds_{-1, -1};
    std::size_t capacity_{0};
};
