#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <cstring>
#include <iostream>
#include <expected>
#include <system_error>
#include <array>

// RAII-обгортка для автоматичного управління життєвим циклом дескрипторів
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
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
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

// Відправка файлового дескриптора через сокет Unix
[[nodiscard]] std::expected<void, std::error_code> send_fd(int socket_fd, int fd_to_send) noexcept {
    struct msghdr msg{};
    struct iovec iov{};
    char dummy_char = 'F';

    alignas(struct cmsghdr) std::array<char, CMSG_SPACE(sizeof(int))> cmsg_buf{};

    iov.iov_base = &dummy_char;
    iov.iov_len = sizeof(dummy_char);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cmsg_buf.data();
    msg.msg_controllen = cmsg_buf.size();

    struct cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));

    std::memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));

    if (::sendmsg(socket_fd, &msg, 0) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

// Отримання переданого дескриптора з сокета Unix
[[nodiscard]] std::expected<UniqueFd, std::error_code> recv_fd(int socket_fd) noexcept {
    struct msghdr msg{};
    struct iovec iov{};
    char dummy_char = 0;
    alignas(struct cmsghdr) std::array<char, CMSG_SPACE(sizeof(int))> cmsg_buf{};

    iov.iov_base = &dummy_char;
    iov.iov_len = sizeof(dummy_char);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cmsg_buf.data();
    msg.msg_controllen = cmsg_buf.size();

    if (::recvmsg(socket_fd, &msg, 0) <= 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    struct cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    if (!cmsg || cmsg->cmsg_level != SOL_SOCKET || cmsg->cmsg_type != SCM_RIGHTS) {
        return std::unexpected(std::make_error_code(std::errc::bad_message));
    }

    int received_fd = -1;
    std::memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));
    return UniqueFd(received_fd);
}
