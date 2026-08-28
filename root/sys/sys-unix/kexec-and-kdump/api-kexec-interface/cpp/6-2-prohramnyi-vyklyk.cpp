#include <iostream>
#include <string>
#include <string_view>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef SYS_kexec_file_load
#define SYS_kexec_file_load 320
#endif

class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd) : fd_(fd) {}
    ~ScopedFd() { if (fd_ >= 0) ::close(fd_); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    ScopedFd& operator=(ScopedFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

void load_kernel(std::string_view kernel_path, std::string_view initrd_path, std::string_view cmdline) {
    ScopedFd kfd(::open(kernel_path.data(), O_RDONLY));
    if (!kfd.valid()) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити ядро");
    }

    ScopedFd ifd(-1);
    if (!initrd_path.empty()) {
        ifd = ScopedFd(::open(initrd_path.data(), O_RDONLY));
        if (!ifd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити initrd");
        }
    }

    const unsigned long cmdlen = cmdline.empty() ? 0 : cmdline.size() + 1;
    const long ret = ::syscall(SYS_kexec_file_load, kfd.get(), ifd.get(), cmdlen, cmdline.data(), 0);

    if (ret < 0) {
        throw std::system_error(errno, std::generic_category(), "kexec_file_load завершився помилкою");
    }

    std::cout << "Ядро успішно завантажено у пам'ять через kexec_file_load\n";
}
