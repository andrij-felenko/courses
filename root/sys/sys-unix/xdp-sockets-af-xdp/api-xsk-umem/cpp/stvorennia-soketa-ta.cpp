#include <sys/socket.h>
#include <linux/if_xdp.h>
#include <system_error>
#include <unistd.h>

class XskSocket {
    int fd_{-1};
public:
    XskSocket() {
        fd_ = ::socket(AF_XDP, SOCK_RAW, 0);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "socket(AF_XDP) failed");
        }
    }
    ~XskSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    XskSocket(const XskSocket&) = delete;
    XskSocket& operator=(const XskSocket&) = delete;
    XskSocket(XskSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    XskSocket& operator=(XskSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};
