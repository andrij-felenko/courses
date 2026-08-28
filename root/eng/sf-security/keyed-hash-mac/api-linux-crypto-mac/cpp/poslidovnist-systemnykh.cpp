#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <expected>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/if_alg.h>

namespace sys_crypto {

class ScopedFd {
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() noexcept { if (fd_ >= 0) ::close(fd_); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_;
};

enum class AlgError {
    SocketCreationFailed,
    BindFailed,
    SetKeyFailed,
    AcceptFailed,
    WriteFailed,
    ReadFailed
};

[[nodiscard]] std::expected<std::array<uint8_t, 32>, AlgError>
af_alg_hmac_sha256(std::span<const uint8_t> key,
                   std::span<const uint8_t> message) noexcept {
    ScopedFd tfm_fd(::socket(AF_ALG, SOCK_SEQPACKET, 0));
    if (!tfm_fd.valid()) {
        return std::unexpected(AlgError::SocketCreationFailed);
    }

    sockaddr_alg sa{};
    sa.salg_family = AF_ALG;
    __builtin_strncpy(reinterpret_cast<char*>(sa.salg_type), "hash", sizeof(sa.salg_type));
    __builtin_strncpy(reinterpret_cast<char*>(sa.salg_name), "hmac(sha256)", sizeof(sa.salg_name));

    if (::bind(tfm_fd.get(), reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
        return std::unexpected(AlgError::BindFailed);
    }

    if (::setsockopt(tfm_fd.get(), SOL_ALG, ALG_SET_KEY, key.data(), key.size()) < 0) {
        return std::unexpected(AlgError::SetKeyFailed);
    }

    ScopedFd op_fd(::accept(tfm_fd.get(), nullptr, nullptr));
    if (!op_fd.valid()) {
        return std::unexpected(AlgError::AcceptFailed);
    }

    if (::write(op_fd.get(), message.data(), message.size()) != static_cast<ssize_t>(message.size())) {
        return std::unexpected(AlgError::WriteFailed);
    }

    std::array<uint8_t, 32> tag{};
    if (::read(op_fd.get(), tag.data(), tag.size()) != static_cast<ssize_t>(tag.size())) {
        return std::unexpected(AlgError::ReadFailed);
    }

    return tag;
}

} // namespace sys_crypto
