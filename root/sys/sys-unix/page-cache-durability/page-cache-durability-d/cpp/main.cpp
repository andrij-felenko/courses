#include <fcntl.h>
#include <unistd.h>
#include <cstdio>
#include <cstddef>
#include <string>
#include <string_view>
#include <span>
#include <utility>

// RAII обгортка для файлового дескриптора
class ScopedFd {
    int fd_ = -1;
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() { if (fd_ >= 0) ::close(fd_); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& o) noexcept : fd_(std::exchange(o.fd_, -1)) {}
    ScopedFd& operator=(ScopedFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = std::exchange(o.fd_, -1);
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] explicit operator bool() const noexcept { return fd_ >= 0; }
    int release() noexcept { return std::exchange(fd_, -1); }
};

// Замінити вміст файлу name у каталозі dir на data (ідоматичний C++)
bool replace_file(std::string_view dir, std::string_view name, std::span<const std::byte> data) {
    const std::string tmp = std::string(dir) + "/." + std::string(name) + ".tmp";
    const std::string final_path = std::string(dir) + "/" + std::string(name);

    ScopedFd fd(::open(tmp.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644));
    if (!fd) return false;

    const char* ptr = reinterpret_cast<const char*>(data.data());
    size_t left = data.size();
    while (left > 0) {
        ssize_t n = ::write(fd.get(), ptr, left);
        if (n < 0) return false;
        ptr += n;
        left -= static_cast<size_t>(n);
    }

    if (::fsync(fd.get()) < 0) return false;

    int raw_fd = fd.release();
    if (::close(raw_fd) < 0) return false;

    if (::rename(tmp.c_str(), final_path.c_str()) < 0) return false;

    ScopedFd dfd(::open(std::string(dir).c_str(), O_RDONLY | O_DIRECTORY));
    if (!dfd) return false;
    return ::fsync(dfd.get()) == 0;
}
