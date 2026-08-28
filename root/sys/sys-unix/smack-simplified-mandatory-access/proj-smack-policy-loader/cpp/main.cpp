#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <system_error>
#include <filesystem>
#include <expected>
#include <array>
#include <fcntl.h>
#include <unistd.h>
#include <sys/xattr.h>

namespace smack {

constexpr std::string_view load2_path = "/sys/fs/smackfs/load2";
constexpr std::string_view access_path = "/sys/fs/smackfs/access2";
constexpr std::string_view xattr_name = "security.SMACK64";

// RAII обгортка для автоматичного закриття файлового дескриптора
class FileDescriptor {
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
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
    int fd_{-1};
};

// Завантаження правила у /sys/fs/smackfs/load2 з використанням std::expected (C++23)
std::expected<void, std::error_code> load_rule(std::string_view subject,
                                                std::string_view object,
                                                std::string_view access) {
    std::string rule = std::string(subject) + " " + std::string(object) + " " + std::string(access) + "\n";

    FileDescriptor fd(::open(load2_path.data(), O_WRONLY));
    if (!fd.valid()) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ssize_t written = ::write(fd.get(), rule.data(), rule.size());
    if (written < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    std::cout << "[C++] Завантажено правило: " << rule;
    return {};
}

// Призначення мітки SMACK на файл
std::expected<void, std::error_code> set_label(const std::filesystem::path& path,
                                                std::string_view label) {
    int res = ::setxattr(path.c_str(), xattr_name.data(), label.data(), label.size(), 0);
    if (res < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    std::cout << "[C++] Призначено мітку '" << label << "' для файла " << path << "\n";
    return {};
}

// Перевірка прав доступу через /sys/fs/smackfs/access2
std::expected<bool, std::error_code> check_access(std::string_view subject,
                                                   std::string_view object,
                                                   std::string_view access_req) {
    std::string query = std::string(subject) + " " + std::string(object) + " " + std::string(access_req);

    FileDescriptor fd(::open(access_path.data(), O_RDWR));
    if (!fd.valid()) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::write(fd.get(), query.data(), query.size()) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ::lseek(fd.get(), 0, SEEK_SET);

    std::array<char, 16> reply_buf{};
    ssize_t bytes_read = ::read(fd.get(), reply_buf.data(), reply_buf.size() - 1);
    if (bytes_read <= 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    bool granted = (reply_buf[0] == '1');
    std::cout << "[C++] Доступ (" << subject << " -> " << object << " [" << access_req << "]): "
              << (granted ? "ДОЗВОЛЕНО" : "ЗАБОРОНЕНО") << "\n";
    return granted;
}

} // namespace smack

int main() {
    const std::filesystem::path test_file = "/tmp/smack_test_cpp.txt";

    // Створення тестового файла через C++ filesystem
    {
        std::ofstream ofs(test_file);
        ofs << "CPP Sample Data\n";
    }

    if (auto res = smack::set_label(test_file, "UserData"); !res) {
        std::cerr << "Помилка встановлення мітки: " << res.error().message() << "\n";
        return 1;
    }

    if (auto res = smack::load_rule("WebBrowser", "UserData", "rw"); !res) {
        std::cerr << "Помилка завантаження правила: " << res.error().message() << "\n";
        return 1;
    }

    auto access_r = smack::check_access("WebBrowser", "UserData", "r");
    auto access_x = smack::check_access("WebBrowser", "UserData", "x");

    if (access_r.has_value() && access_x.has_value()) {
        std::cout << "Обидва запити до ядра виконано; 'x' очікувано заборонено правилом rw.\n";
    }

    return 0;
}
