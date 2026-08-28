// Приклад виклику криптопідсистеми з простору користувача через сокети AF_ALG (C++20)
#include <array>
#include <cstdint>
#include <cstring>
#include <span>
#include <stdexcept>
#include <sys/socket.h>
#include <linux/if_alg.h>
#include <unistd.h>

namespace crypto {

class LinuxAfAlgHmac {
public:
    explicit LinuxAfAlgHmac(std::span<const uint8_t> key) {
        sock_ = socket(AF_ALG, SOCK_SEQPACKET, 0);
        if (sock_ < 0) throw std::runtime_error("Не вдалося відкрити AF_ALG сокет");

        struct sockaddr_alg sa{};
        sa.salg_family = AF_ALG;
        std::strcpy(reinterpret_cast<char*>(sa.salg_type), "hash");
        std::strcpy(reinterpret_cast<char*>(sa.salg_name), "hmac(sha256)");

        if (bind(sock_, reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            close(sock_);
            throw std::runtime_error("Помилка bind AF_ALG hmac(sha256)");
        }
        if (setsockopt(sock_, SOL_ALG, ALG_SET_KEY, key.data(), key.size()) < 0) {
            close(sock_);
            throw std::runtime_error("Помилка встановлення ключа ALG_SET_KEY");
        }
        op_sock_ = accept(sock_, nullptr, nullptr);
        if (op_sock_ < 0) {
            close(sock_);
            throw std::runtime_error("Помилка accept AF_ALG");
        }
    }

    ~LinuxAfAlgHmac() {
        if (op_sock_ >= 0) close(op_sock_);
        if (sock_ >= 0) close(sock_);
    }

    [[nodiscard]] std::array<uint8_t, 32> sign(std::span<const uint8_t> data) {
        if (write(op_sock_, data.data(), data.size()) < 0) {
            throw std::runtime_error("Помилка запису даних у AF_ALG сокет");
        }
        std::array<uint8_t, 32> out{};
        if (read(op_sock_, out.data(), out.size()) != static_cast<ssize_t>(out.size())) {
            throw std::runtime_error("Помилка читання підпису з AF_ALG сокета");
        }
        return out;
    }

private:
    int sock_{-1};
    int op_sock_{-1};
};

} // namespace crypto
