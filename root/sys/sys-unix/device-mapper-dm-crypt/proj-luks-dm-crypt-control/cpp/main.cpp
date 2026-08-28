#include <iostream>
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <cstring>
#include <cstdlib>
#include <libcryptsetup.h>

// RAII кастомний видаляч для struct crypt_device
struct CryptDeviceDeleter {
    void operator()(crypt_device* cd) const noexcept {
        if (cd) {
            crypt_free(cd);
        }
    }
};

using CryptDevicePtr = std::unique_ptr<crypt_device, CryptDeviceDeleter>;

class LuksVolume {
public:
    // Фабричний метод відкриття зашифрованого пристрою
    static std::expected<LuksVolume, std::string> open(std::string_view device_path) {
        crypt_device* raw_cd = nullptr;
        int r = crypt_init(&raw_cd, device_path.data());
        if (r < 0) {
            return std::unexpected(std::string("crypt_init failed: ") + std::strerror(-r));
        }

        CryptDevicePtr cd(raw_cd);

        r = crypt_load(cd.get(), CRYPT_LUKS, nullptr);
        if (r < 0) {
            return std::unexpected(std::string("crypt_load failed: ") + std::strerror(-r));
        }

        return LuksVolume(std::move(cd));
    }

    // Метод аутентифікації та активації відображення
    [[nodiscard]] std::expected<int, std::string> activate(std::string_view target_name, 
                                                            std::string_view passphrase) const {
        int slot = crypt_activate_by_passphrase(
            cd_.get(),
            target_name.data(),
            CRYPT_ANY_SLOT,
            passphrase.data(),
            passphrase.size(),
            0
        );

        if (slot < 0) {
            return std::unexpected(std::string("Активація відхилена: ") + std::strerror(-slot));
        }

        return slot;
    }

    [[nodiscard]] std::string_view type() const noexcept {
        const char* t = crypt_get_type(cd_.get());
        return t ? std::string_view(t) : std::string_view("unknown");
    }

    [[nodiscard]] std::string_view uuid() const noexcept {
        const char* u = crypt_get_uuid(cd_.get());
        return u ? std::string_view(u) : std::string_view("");
    }

private:
    explicit LuksVolume(CryptDevicePtr cd) : cd_(std::move(cd)) {}
    CryptDevicePtr cd_;
};

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Використання: " << argv[0] << " <пристрій> <ім'я_відображення> <пароль>\n";
        return EXIT_FAILURE;
    }

    const std::string_view device_path = argv[1];
    const std::string_view target_name = argv[2];
    const std::string_view passphrase = argv[3];

    auto volume_result = LuksVolume::open(device_path);
    if (!volume_result) {
        std::cerr << "Помилка відкриття LUKS тома: " << volume_result.error() << '\n';
        return EXIT_FAILURE;
    }

    const auto& volume = *volume_result;
    std::cout << "Успішно відкрито том LUKS!\n";
    std::cout << "Тип заголовка: " << volume.type() << "\nUUID тома:     " << volume.uuid() << '\n';

    auto activation_result = volume.activate(target_name, passphrase);
    if (!activation_result) {
        std::cerr << "Помилка активації: " << activation_result.error() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "Пристрій успішно активовано: /dev/mapper/" << target_name
              << " (слот ключа " << *activation_result << ")\n";

    return EXIT_SUCCESS;
}
