// kexec_runner.cpp — Ідіоматична реалізація мовою C++20 (RAII, std::expected, std::string_view)
#include <iostream>
#include <fstream>
#include <string_view>
#include <system_error>
#include <expected>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/reboot.h>
#include <linux/kexec.h>

#ifndef SYS_kexec_file_load
#if defined(__x86_64__)
#define SYS_kexec_file_load 320
#elif defined(__aarch64__)
#define SYS_kexec_file_load 294
#endif
#endif

namespace sys {

// RAII обгортка для автоматичного управління файловими дескрипторами
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_{-1};
};

} // namespace sys

class KexecLoader {
public:
    static bool is_kexec_loaded() noexcept {
        std::ifstream status_file("/sys/kernel/kexec_loaded");
        int value = 0;
        return (status_file >> value) && (value == 1);
    }

    static std::expected<void, std::error_code> load_kernel(
        std::string_view kernel_path,
        std::string_view initrd_path,
        std::string_view cmdline,
        unsigned long flags = 0) noexcept
    {
        sys::UniqueFd kernel_fd(::open(kernel_path.data(), O_RDONLY | O_CLOEXEC));
        if (!kernel_fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        sys::UniqueFd initrd_fd;
        if (!initrd_path.empty()) {
            initrd_fd.reset(::open(initrd_path.data(), O_RDONLY | O_CLOEXEC));
            if (!initrd_fd.valid()) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
        }

        const int raw_initrd_fd = initrd_fd.valid() ? initrd_fd.get() : -1;
        const size_t cmdline_len = cmdline.empty() ? 0 : cmdline.size() + 1;
        const char* cmdline_ptr = cmdline.empty() ? nullptr : cmdline.data();

        long ret = ::syscall(SYS_kexec_file_load, kernel_fd.get(), raw_initrd_fd, cmdline_len, cmdline_ptr, flags);
        if (ret != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Використання: " << argv[0] << " <path_to_vmlinuz> [path_to_initrd] [cmdline]\n";
        return 1;
    }

    if (KexecLoader::is_kexec_loaded()) {
        std::cout << "Увага: У системі вже завантажено ядро через kexec.\n";
    }

    const std::string_view kernel_path = argv[1];
    const std::string_view initrd_path = (argc > 2) ? argv[2] : "";
    const std::string_view cmdline = (argc > 3) ? argv[3] : "console=tty0 quiet";

    auto result = KexecLoader::load_kernel(kernel_path, initrd_path, cmdline);
    if (!result) {
        std::cerr << "Помилка завантаження ядра через kexec: " << result.error().message() << '\n';
        return 1;
    }

    std::cout << "Ядро успішно завантажено в пам'ять! Ресурси закриті автоматично RAII.\n";
    std::cout << "Для активації нового ядра виконайте системний виклик reboot.\n";
    return 0;
}
