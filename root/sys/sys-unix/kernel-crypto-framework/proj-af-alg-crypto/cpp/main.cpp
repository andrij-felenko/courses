#include <iostream>
#include <iomanip>
#include <algorithm>
#include <array>
#include <span>
#include <string_view>
#include <system_error>
#include <cerrno>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/if_alg.h>

#ifndef SOL_ALG
#define SOL_ALG 279
#endif

// RAII обгортка для файлового дескриптора сокета
class UniqueFd {
    int fd_ = -1;
public:
    explicit UniqueFd(int fd = -1) : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

class KernelCrypto {
public:
    static std::array<uint8_t, 32> sha256(std::span<const uint8_t> input) {
        UniqueFd tfm_fd(::socket(AF_ALG, SOCK_SEQPACKET, 0));
        if (!tfm_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка створення сокета AF_ALG");
        }

        struct sockaddr_alg sa{};
        sa.salg_family = AF_ALG;
        std::string_view type = "hash";
        std::string_view name = "sha256";
        std::copy(type.begin(), type.end(), sa.salg_type);
        std::copy(name.begin(), name.end(), sa.salg_name);

        if (::bind(tfm_fd.get(), reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка bind(AF_ALG)");
        }

        UniqueFd op_fd(::accept(tfm_fd.get(), nullptr, nullptr));
        if (!op_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка accept(AF_ALG)");
        }

        if (::write(op_fd.get(), input.data(), input.size()) != static_cast<ssize_t>(input.size())) {
            throw std::system_error(errno, std::generic_category(), "Помилка запису даних у сокет");
        }

        std::array<uint8_t, 32> digest{};
        if (::read(op_fd.get(), digest.data(), digest.size()) != static_cast<ssize_t>(digest.size())) {
            throw std::system_error(errno, std::generic_category(), "Помилка читання дайджесту з сокета");
        }

        return digest;
    }
};

int main() {
    try {
        std::string_view msg = "Hello, Kernel Crypto API!";
        auto input = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(msg.data()), msg.size());
        auto hash = KernelCrypto::sha256(input);

        std::cout << "SHA-256 дайджест (C++20 RAII): ";
        for (uint8_t byte : hash) {
            std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
        }
        std::cout << std::dec << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
