#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <array>
#include <memory>
#include <system_error>
#include <expected>
#include <cstring>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>

namespace zfs {

constexpr std::string_view kZfsDevPath = "/dev/zfs";
constexpr size_t kKeySizeBytes = 32;

/* RAII-обгортка для безпечного управління файл-дескриптором /dev/zfs */
class ZfsControlDevice {
public:
    ZfsControlDevice() {
        fd_ = ::open(kZfsDevPath.data(), O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити " + std::string(kZfsDevPath));
        }
    }

    ~ZfsControlDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    ZfsControlDevice(const ZfsControlDevice&) = delete;
    ZfsControlDevice& operator=(const ZfsControlDevice&) = delete;

    ZfsControlDevice(ZfsControlDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

/* Спрощена структура ioctl ZFS */
struct ZfsCmdArgs {
    char zc_name[256]{};
    char zc_value[1024]{};
    uint64_t zc_cookie{0};
    uint64_t zc_objset_type{0};
    uint64_t zc_keystatus{0};
    uint64_t zc_keyformat{0};
};

using KeyBuffer = std::array<uint8_t, kKeySizeBytes>;

/* Зчитати бінарний ключ із безпечним витиранням пам'яті в деструкторі */
class SecureKeyBuffer {
public:
    SecureKeyBuffer() = default;
    ~SecureKeyBuffer() {
        ::explicit_bzero(buffer_.data(), buffer_.size());
    }

    [[nodiscard]] KeyBuffer& data() noexcept { return buffer_; }
    [[nodiscard]] const KeyBuffer& data() const noexcept { return buffer_; }

private:
    KeyBuffer buffer_{};
};

/* Безпечне зчитування ключа із використанням std::expected (C++23) */
std::expected<SecureKeyBuffer, std::string> ReadRawKeyFile(std::string_view key_path) {
    std::ifstream file(key_path.data(), std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected("Не вдалося відкрити файл ключа: " + std::string(key_path));
    }

    SecureKeyBuffer key_buf;
    file.read(reinterpret_cast<char*>(key_buf.data().data()), kKeySizeBytes);
    if (static_cast<size_t>(file.gcount()) != kKeySizeBytes) {
        return std::unexpected("Некоректний розмір ключа у файлі (очікувалося 32 байти)");
    }

    return key_buf;
}

/* Завантаження майстер-ключа в ядро Linux через ioctl */
std::expected<void, std::string> LoadDatasetKey(const ZfsControlDevice& zfs_dev, 
                                                std::string_view dataset_name, 
                                                const SecureKeyBuffer& key) {
    ZfsCmdArgs cmd{};
    std::strncpy(cmd.zc_name, dataset_name.data(), sizeof(cmd.zc_name) - 1);
    cmd.zc_keyformat = 1; // Raw 256-bit binary
    std::memcpy(cmd.zc_value, key.data().data(), kKeySizeBytes);

    if (::ioctl(zfs_dev.get(), 0x5a01, &cmd) != 0) {
        if (errno == EEXIST) {
            return {}; // Ключ вже завантажено
        }
        return std::unexpected("Помилка ioctl ZFS_IOC_LOAD_KEY: " + std::string(std::strerror(errno)));
    }

    return {};
}

} // namespace zfs

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <dataset_name> <key_file_path>\n";
        return EXIT_FAILURE;
    }

    const std::string_view dataset_name = argv[1];
    const std::string_view key_file_path = argv[2];

    try {
        zfs::ZfsControlDevice zfs_dev;
        
        auto key_result = zfs::ReadRawKeyFile(key_file_path);
        if (!key_result) {
            std::cerr << "Помилка зчитування ключа: " << key_result.error() << '\n';
            return EXIT_FAILURE;
        }

        auto load_result = zfs::LoadDatasetKey(zfs_dev, dataset_name, *key_result);
        if (!load_result) {
            std::cerr << "Помилка завантаження ключа в ядро: " << load_result.error() << '\n';
            return EXIT_FAILURE;
        }

        std::cout << "Майстер-ключ ZFS успішно завантажено для " << dataset_name << '\n';
    } catch (const std::exception& ex) {
        std::cerr << "Фатальна помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
