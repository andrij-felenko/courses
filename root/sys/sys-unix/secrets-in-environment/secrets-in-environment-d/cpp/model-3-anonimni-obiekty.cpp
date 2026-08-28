// Створення запечатаного буфера memfd мовою C++ з використанням std::span
#define _GNU_SOURCE
#include <sys/mman.h>
#include <unistd.h>
#include <fcntl.h>
#include <string_view>
#include <span>
#include <optional>
#include <iostream>

class SealedSecretBuffer {
    int fd_{-1};
public:
    explicit SealedSecretBuffer(int fd) noexcept : fd_(fd) {}
    ~SealedSecretBuffer() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SealedSecretBuffer(const SealedSecretBuffer&) = delete;
    SealedSecretBuffer& operator=(const SealedSecretBuffer&) = delete;

    SealedSecretBuffer(SealedSecretBuffer&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SealedSecretBuffer& operator=(SealedSecretBuffer&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int descriptor() const noexcept { return fd_; }

    static std::optional<SealedSecretBuffer> create(std::string_view secret_data) noexcept {
        int fd = ::memfd_create("cpp_sealed_secret", MFD_CLOEXEC | MFD_ALLOW_SEALING);
        if (fd < 0) return std::nullopt;

        if (::ftruncate(fd, static_cast<off_t>(secret_data.size())) < 0) {
            ::close(fd);
            return std::nullopt;
        }

        if (::write(fd, secret_data.data(), secret_data.size()) != static_cast<ssize_t>(secret_data.size())) {
            ::close(fd);
            return std::nullopt;
        }

        // Встановлюємо пломби
        constexpr int seals = F_SEAL_WRITE | F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL;
        if (::fcntl(fd, F_ADD_SEALS, seals) < 0) {
            ::close(fd);
            return std::nullopt;
        }

        ::lseek(fd, 0, SEEK_SET);
        return SealedSecretBuffer(fd);
    }
};
