// Ідіоматична обгортка для Linux Kernel Keyring у C++
#define _GNU_SOURCE
#include <iostream>
#include <string_view>
#include <vector>
#include <optional>
#include <system_error>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/keyctl.h>

class KernelKeyringSecret {
    int32_t key_id_{-1};
public:
    explicit KernelKeyringSecret(int32_t key_id) noexcept : key_id_(key_id) {}
    ~KernelKeyringSecret() {
        if (key_id_ > 0) {
            // Відкликаємо ключ при знищенні об'єкта
            ::syscall(__NR_keyctl, KEYCTL_REVOKE, key_id_, 0, 0, 0);
        }
    }

    KernelKeyringSecret(const KernelKeyringSecret&) = delete;
    KernelKeyringSecret& operator=(const KernelKeyringSecret&) = delete;

    KernelKeyringSecret(KernelKeyringSecret&& o) noexcept : key_id_(o.key_id_) {
        o.key_id_ = -1;
    }
    KernelKeyringSecret& operator=(KernelKeyringSecret&& o) noexcept {
        if (this != &o) {
            if (key_id_ > 0) ::syscall(__NR_keyctl, KEYCTL_REVOKE, key_id_, 0, 0, 0);
            key_id_ = o.key_id_;
            o.key_id_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int32_t id() const noexcept { return key_id_; }

    static std::optional<KernelKeyringSecret> store(std::string_view name, std::string_view payload, unsigned int timeout_sec = 300) noexcept {
        auto res = ::syscall(__NR_add_key, "user", name.data(), payload.data(), payload.size(), KEY_SPEC_PROCESS_KEYRING);
        if (res < 0) return std::nullopt;

        const auto key_id = static_cast<int32_t>(res);
        if (timeout_sec > 0) {
            ::syscall(__NR_keyctl, KEYCTL_SET_TIMEOUT, key_id, timeout_sec, 0, 0);
        }
        return KernelKeyringSecret(key_id);
    }

    [[nodiscard]] std::optional<std::vector<char>> read() const noexcept {
        if (key_id_ <= 0) return std::nullopt;

        auto len = ::syscall(__NR_keyctl, KEYCTL_READ, key_id_, nullptr, 0, 0);
        if (len <= 0) return std::nullopt;

        std::vector<char> buffer(static_cast<std::size_t>(len));
        auto read_len = ::syscall(__NR_keyctl, KEYCTL_READ, key_id_, buffer.data(), buffer.size(), 0);
        if (read_len != len) return std::nullopt;

        return buffer;
    }
};

int main() {
    auto secret = KernelKeyringSecret::store("jwt_signing_key", "SuperSecretPayload2026", 600);
    if (!secret) {
        std::cerr << "Не вдалося зберегти ключ у Kernel Keyring\n";
        return EXIT_FAILURE;
    }

    std::cout << "Ключ успішно зареєстровано в ядрі, Key ID: " << secret->id() << '\n';

    auto retrieved = secret->read();
    if (retrieved) {
        std::cout << "Успішно зчитано ключ довжиною " << retrieved->size() << " байтів\n";
        // Занулення пам'яті після використання
        ::explicit_bzero(retrieved->data(), retrieved->size());
    }

    return EXIT_SUCCESS;
}
