#include <sys/socket.h>
#include <linux/if_alg.h>
#include <unistd.h>
#include <cstring>
#include <cstdint>
#include <array>
#include <span>
#include <expected>
#include <memory>

namespace kernel_crypto {

enum class AlgError {
    kSocketCreationFailed,
    kBindFailed,
    kSetKeyFailed,
    kAcceptFailed,
    kSendFailed,
    kReadFailed,
    kInvalidInput
};

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

class KernelXtsCipher {
public:
    [[nodiscard]] static std::expected<KernelXtsCipher, AlgError> Create(
        std::span<const uint8_t, 64> key_512bit) noexcept {

        ScopedFd tfm_fd(::socket(AF_ALG, SOCK_SEQPACKET, 0));
        if (!tfm_fd.valid()) return std::unexpected(AlgError::kSocketCreationFailed);

        struct sockaddr_alg sa{};
        sa.salg_family = AF_ALG;
        std::strncpy(reinterpret_cast<char*>(sa.salg_type), "skcipher", sizeof(sa.salg_type) - 1);
        std::strncpy(reinterpret_cast<char*>(sa.salg_name), "xts(aes)", sizeof(sa.salg_name) - 1);

        if (::bind(tfm_fd.get(), reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            return std::unexpected(AlgError::kBindFailed);
        }

        if (::setsockopt(tfm_fd.get(), SOL_ALG, ALG_SET_KEY, key_512bit.data(), key_512bit.size()) < 0) {
            return std::unexpected(AlgError::kSetKeyFailed);
        }

        ScopedFd op_fd(::accept(tfm_fd.get(), nullptr, 0));
        if (!op_fd.valid()) return std::unexpected(AlgError::kAcceptFailed);

        return KernelXtsCipher(std::move(op_fd));
    }

    [[nodiscard]] std::expected<void, AlgError> Process(
        std::span<const uint8_t, 16> tweak_128bit,
        std::span<const uint8_t> input,
        std::span<uint8_t> output,
        uint32_t operation) const noexcept {

        if (input.size() < 16 || output.size() < input.size()) {
            return std::unexpected(AlgError::kInvalidInput);
        }

        alignas(struct cmsghdr) char cbuf[CMSG_SPACE(sizeof(uint32_t)) + CMSG_SPACE(sizeof(struct af_alg_iv) + 16)]{};
        struct msghdr msg{};
        msg.msg_control = cbuf;
        msg.msg_controllen = sizeof(cbuf);

        struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
        cmsg->cmsg_level = SOL_ALG;
        cmsg->cmsg_type = ALG_SET_OP;
        cmsg->cmsg_len = CMSG_LEN(sizeof(uint32_t));
        *reinterpret_cast<uint32_t*>(CMSG_DATA(cmsg)) = operation;

        cmsg = CMSG_NXTHDR(&msg, cmsg);
        cmsg->cmsg_level = SOL_ALG;
        cmsg->cmsg_type = ALG_SET_IV;
        cmsg->cmsg_len = CMSG_LEN(sizeof(struct af_alg_iv) + 16);
        auto *iv_hdr = reinterpret_cast<struct af_alg_iv*>(CMSG_DATA(cmsg));
        iv_hdr->ivlen = 16;
        std::memcpy(iv_hdr->iv, tweak_128bit.data(), 16);

        struct iovec iov{};
        iov.iov_base = const_cast<uint8_t*>(input.data());
        iov.iov_len = input.size();
        msg.msg_iov = &iov;
        msg.msg_iovlen = 1;

        if (::sendmsg(op_fd_.get(), &msg, 0) < 0) {
            return std::unexpected(AlgError::kSendFailed);
        }

        const ssize_t bytes_read = ::read(op_fd_.get(), output.data(), input.size());
        if (bytes_read != static_cast<ssize_t>(input.size())) {
            return std::unexpected(AlgError::kReadFailed);
        }

        return {};
    }

private:
    explicit KernelXtsCipher(ScopedFd op_fd) noexcept : op_fd_(std::move(op_fd)) {}
    ScopedFd op_fd_;
};

} // namespace kernel_crypto
