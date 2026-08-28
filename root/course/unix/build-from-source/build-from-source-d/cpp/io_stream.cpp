// io_stream.cpp — Ідіоматична C++ реалізація з RAII та std::expected
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <string_view>
#include <system_error>
#include <expected>
#include <fcntl.h>
#include <unistd.h>

class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd) noexcept : fd_{fd} {}
    ~UniqueFd() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    UniqueFd(UniqueFd&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) {
                ::close(fd_);
            }
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

std::expected<UniqueFd, std::error_code> open_nonblocking_stream(std::string_view path) {
#if defined(HAVE_O_NONBLOCK) && defined(O_CLOEXEC)
    int fd = ::open(path.data(), O_RDONLY | O_NONBLOCK | O_CLOEXEC);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return UniqueFd{fd};
#else
    int fd = ::open(path.data(), O_RDONLY);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    UniqueFd ufd{fd};
    int flags = ::fcntl(ufd.get(), F_GETFL, 0);
    if (flags == -1 || ::fcntl(ufd.get(), F_SETFL, flags | O_NONBLOCK) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return ufd;
#endif
}
