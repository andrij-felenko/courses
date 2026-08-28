#include <sys/socket.h>
#include <netpacket/packet.h>
#include <net/ethernet.h>
#include <arpa/inet.h>
#include <linux/filter.h>
#include <unistd.h>
#include <expected>
#include <optional>

namespace net {

class PacketCaptureSocket {
public:
    explicit PacketCaptureSocket(int fd = -1) noexcept : fd_{fd} {}
    ~PacketCaptureSocket() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }

    PacketCaptureSocket(const PacketCaptureSocket&) = delete;
    PacketCaptureSocket& operator=(const PacketCaptureSocket&) = delete;
    PacketCaptureSocket(PacketCaptureSocket&& o) noexcept : fd_{o.fd_} { o.fd_ = -1; }
    PacketCaptureSocket& operator=(PacketCaptureSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] static std::expected<PacketCaptureSocket, int> create(
        const std::optional<sock_fprog>& bpf_prog = std::nullopt) noexcept 
    {
        const int fd = ::socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
        if (fd < 0) {
            return std::unexpected(errno);
        }

        if (bpf_prog.has_value()) {
            if (::setsockopt(fd, SOL_SOCKET, SO_ATTACH_FILTER, 
                             &*bpf_prog, sizeof(*bpf_prog)) < 0) {
                const int err = errno;
                ::close(fd);
                return std::unexpected(err);
            }
        }
        return PacketCaptureSocket{fd};
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

} // namespace net
