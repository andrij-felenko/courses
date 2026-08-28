#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

class SocketHandle {
    int fd_ = -1;
public:
    explicit SocketHandle(int fd = -1) : fd_(fd) {}
    ~SocketHandle() {
        if (fd_ >= 0) ::close(fd_);
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    void configure() const {
        int flags = ::fcntl(fd_, F_GETFL, 0);
        if (flags >= 0) ::fcntl(fd_, F_SETFL, flags | O_NONBLOCK);
        int one = 1;
        ::setsockopt(fd_, IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one));
    }
    void shutdownWrite() const noexcept {
        if (fd_ >= 0) ::shutdown(fd_, SHUT_WR);
    }
};

/* Ідіоматичний L4-міст на базі C++ RAII та std::span */
void l4BridgeLoopCpp(const SocketHandle& client, const SocketHandle& backend) {
    client.configure();
    backend.configure();

    std::array<pollfd, 2> fds{{
        {client.get(), POLLIN, 0},
        {backend.get(), POLLIN, 0}
    }};

    std::array<char, 16384> buffer{};

    auto forwardData = [](int src, int dst, std::span<char> buf) -> bool {
        ssize_t n = ::read(src, buf.data(), buf.size());
        if (n > 0) {
            ssize_t written = 0;
            while (written < n) {
                ssize_t w = ::write(dst, buf.data() + written, n - written);
                if (w <= 0) {
                    if (errno == EAGAIN || errno == EWOULDBLOCK) continue;
                    return false;
                }
                written += w;
            }
            return true;
        }
        return n == 0 ? false : (errno == EAGAIN);
    };

    while (true) {
        int ret = ::poll(fds.data(), fds.size(), 5000);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }
        if (ret == 0) continue;

        if (fds[0].revents & POLLIN) {
            if (!forwardData(client.get(), backend.get(), buffer)) {
                backend.shutdownWrite();
                fds[0].events = 0;
            }
        }
        if (fds[1].revents & POLLIN) {
            if (!forwardData(backend.get(), client.get(), buffer)) {
                client.shutdownWrite();
                fds[1].events = 0;
            }
        }

        if ((fds[0].revents & (POLLERR | POLLHUP)) ||
            (fds[1].revents & (POLLERR | POLLHUP)) ||
            (fds[0].events == 0 && fds[1].events == 0)) {
            break;
        }
    }
}
