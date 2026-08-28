#include <iostream>
#include <string>
#include <span>
#include <system_error>
#include <expected>
#include <cstddef>
#include <keyutils.h>

/* Обгортка C++ RAII для управління ключем ядра */
class KernelKey {
public:
    explicit KernelKey(key_serial_t id) : id_(id) {}
    ~KernelKey() {
        if (id_ > 0) {
            /* Автоматичне анулювання ключа при виході з області видимості */
            keyctl(KEYCTL_REVOKE, id_);
        }
    }

    KernelKey(const KernelKey&) = delete;
    KernelKey& operator=(const KernelKey&) = delete;
    KernelKey(KernelKey&& other) noexcept : id_(other.id_) { other.id_ = 0; }

    [[nodiscard]] key_serial_t id() const noexcept { return id_; }

private:
    key_serial_t id_{0};
};

/* Створення logon ключа з використанням std::span та std::expected */
std::expected<KernelKey, std::error_code> store_logon_secret_cpp(
    const std::string& description,
    std::span<const std::byte> payload
) {
    key_serial_t key_id = add_key(
        "logon",
        description.c_str(),   /* add_key чекає C-рядок із нулем на кінці */
        payload.data(),
        payload.size(),
        KEY_SPEC_SESSION_KEYRING
    );

    if (key_id == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return KernelKey{key_id};
}
