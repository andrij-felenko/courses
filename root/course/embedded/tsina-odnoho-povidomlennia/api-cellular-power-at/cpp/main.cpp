#include <zephyr/net/socket.h>
#include <span>
#include <expected>

class RaiSocket {
private:
    int fd_{-1};

public:
    constexpr explicit RaiSocket(int fd) noexcept : fd_{fd} {}

    [[nodiscard]] std::expected<size_t, int> send_with_immediate_release(
        std::span<const uint8_t> payload,
        const sockaddr_in& dest) noexcept {
        const ssize_t res = sendto(
            fd_,
            payload.data(),
            payload.size(),
            MSG_DONTWAIT | RAI_FLAG_NO_REPLY,
            reinterpret_cast<const sockaddr*>(&dest),
            sizeof(dest)
        );
        if (res < 0) {
            return std::unexpected(errno);
        }
        return static_cast<size_t>(res);
    }
};
