/* durable-replace.cpp — заміна вмісту файлу, що переживає збій.
   збірка: g++ -O2 -Wall -Wextra -std=c++20 -o durable-replace durable-replace.cpp */
#define _GNU_SOURCE
#include <cerrno>
#include <climits>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string>
#include <string_view>
#include <span>
#include <system_error>
#include <utility>

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

static int write_all(int fd, std::span<const std::byte> data) {
    const char* ptr = reinterpret_cast<const char*>(data.data());
    size_t len = data.size();
    while (len > 0) {
        ssize_t n = ::write(fd, ptr, len);
        if (n < 0) {
            if (errno == EINTR) continue;
            return errno;
        }
        if (n == 0) return EIO;
        ptr += static_cast<size_t>(n);
        len -= static_cast<size_t>(n);
    }
    return 0;
}

static int fsync_checked(int fd) {
    while (::fsync(fd) != 0)
        if (errno != EINTR) return errno;
    return 0;
}

int durable_replace(std::string_view dir, std::string_view name,
                    std::span<const std::byte> data) {
    std::string dir_str(dir);
    std::string name_str(name);

    ScopedFd dfd(::open(dir_str.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC));
    if (!dfd) return errno;

    char tmp[NAME_MAX + 1];
    ScopedFd fd;
    bool have_tmp = false;

    for (unsigned attempt = 0; ; attempt++) {
        int k = std::snprintf(tmp, sizeof(tmp), ".%s.%ld.%u.tmp",
                              name_str.c_str(), static_cast<long>(::getpid()), attempt);
        if (k < 0 || static_cast<size_t>(k) >= sizeof(tmp)) return ENAMETOOLONG;

        fd = ScopedFd(::openat(dfd.get(), tmp, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600));
        if (fd) break;
        if (errno != EEXIST || attempt >= 1000) return errno;
    }
    have_tmp = true;

    auto cleanup = [&]() {
        if (have_tmp) ::unlinkat(dfd.get(), tmp, 0);
    };

    struct stat st{};
    if (::fstatat(dfd.get(), name_str.c_str(), &st, 0) == 0) {
        if (::fchmod(fd.get(), st.st_mode & 07777) != 0) {
            int err = errno; cleanup(); return err;
        }
    } else if (errno != ENOENT) {
        int err = errno; cleanup(); return err;
    }

    if (int rc = write_all(fd.get(), data); rc != 0) {
        cleanup(); return rc;
    }

    if (int rc = fsync_checked(fd.get()); rc != 0) {
        cleanup(); return rc;
    }

    int raw_fd = fd.release();
    if (::close(raw_fd) != 0) {
        int err = errno; cleanup(); return err;
    }

    if (::renameat(dfd.get(), tmp, dfd.get(), name_str.c_str()) != 0) {
        int err = errno; cleanup(); return err;
    }
    have_tmp = false;

    return fsync_checked(dfd.get());
}

int main(int argc, char** argv) {
    if (argc < 4) {
        std::fprintf(stderr, "вжиток: %s <каталог> <ім'я> <рядок>\n", argv[0]);
        return 2;
    }
    std::string_view text(argv[3]);
    auto bytes = std::span(reinterpret_cast<const std::byte*>(text.data()), text.size());
    int rc = durable_replace(argv[1], argv[2], bytes);
    if (rc != 0) {
        std::fprintf(stderr, "заміна не вдалася: %s\n", std::strerror(rc));
        return 1;
    }
    return 0;
}
