#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <system_error>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/file.h>

namespace fs = std::filesystem;

class SystemLock {
    int lock_fd_{-1};
    fs::path lock_path_;
public:
    explicit SystemLock(fs::path lock_path) : lock_path_(std::move(lock_path)) {
        lock_fd_ = ::open(lock_path_.c_str(), O_RDWR | O_CREAT, 0600);
        if (lock_fd_ < 0 || ::flock(lock_fd_, LOCK_EX | LOCK_NB) < 0) {
            throw std::runtime_error("Не вдалося захопити системне блокування");
        }
    }

    ~SystemLock() {
        if (lock_fd_ >= 0) {
            ::flock(lock_fd_, LOCK_UN);
            ::close(lock_fd_);
            fs::remove(lock_path_);
        }
    }

    SystemLock(const SystemLock&) = delete;
    SystemLock& operator=(const SystemLock&) = delete;
};

class AtomicPackageInstaller {
public:
    static bool install_file(const fs::path& target_path, std::string_view payload, mode_t mode = 0755) {
        fs::path temp_path = target_path;
        temp_path += ".dpkg-new";

        // RAII відкриття та закриття файлового дескриптора
        int fd = ::open(temp_path.c_str(), O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW, mode);
        if (fd < 0) {
            std::cerr << "[ERROR] Помилка відкриття " << temp_path << ": "
                      << std::strerror(errno) << '\n';
            return false;
        }

        struct FdGuard {
            int handle;
            ~FdGuard() { if (handle >= 0) ::close(handle); }
        } fd_guard{fd};

        // Запис даних у файл
        ssize_t written = ::write(fd, payload.data(), payload.size());
        if (written < 0 || static_cast<size_t>(written) != payload.size()) {
            std::cerr << "[ERROR] Збій запису даних у " << temp_path << '\n';
            fs::remove(temp_path);
            return false;
        }

        // Примусовий скид дискових буферів (fsync)
        if (::fsync(fd) < 0) {
            std::cerr << "[ERROR] Помилка fsync для " << temp_path << '\n';
            fs::remove(temp_path);
            return false;
        }

        ::close(fd_guard.handle);
        fd_guard.handle = -1;

        // Атомарна заміна через std::filesystem::rename
        std::error_code ec;
        fs::rename(temp_path, target_path, ec);
        if (ec) {
            std::cerr << "[ERROR] Не вдалося замінити " << target_path 
                      << ": " << ec.message() << '\n';
            fs::remove(temp_path, ec);
            return false;
        }

        std::cout << "[SUCCESS] Успішно інстальовано " << target_path << '\n';
        return true;
    }
};

int main() {
    try {
        SystemLock lock("/tmp/pkg_installer_cpp.lock");

        fs::path target = "/tmp/my_app_binary_cpp";
        std::string_view payload = "#!/bin/sh\necho 'Hello from C++ Atomic Package!'\n";

        return AtomicPackageInstaller::install_file(target, payload) ? 0 : 1;
    } catch (const std::exception& e) {
        std::cerr << "[FATAL] " << e.what() << '\n';
        return 1;
    }
}
