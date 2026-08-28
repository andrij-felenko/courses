#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <string_view>
#include <cstdint>
#include <cerrno>
#include <cstdlib>
#include <system_error>
#include <expected>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/stat.h>

namespace fs_walker {

constexpr std::size_t BufferSize = 64 * 1024;

struct linux_dirent64 {
    std::uint64_t  d_ino;
    std::int64_t   d_off;
    std::uint16_t  d_reclen;
    std::uint8_t   d_type;
    char           d_name[];
};

struct TraversalStats {
    std::size_t files_count{0};
    std::size_t dirs_count{0};
};

class ScopedFd {
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() { if (fd_ != -1) ::close(fd_); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            if (fd_ != -1) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ != -1; }

private:
    int fd_{-1};
};

class DirectoryWalker {
public:
    static std::expected<TraversalStats, std::error_code> walk(const std::string& root_path) {
        ScopedFd root_fd(::open(root_path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC));
        if (!root_fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        DirectoryWalker walker;
        walker.process_fd(root_fd.get());
        return walker.stats_;
    }

private:
    DirectoryWalker() = default;

    void process_fd(int dir_fd) {
        // Буфер власний на кожен рівень рекурсії: спільний перезаписався б
        // вкладеним викликом, і батьківський цикл дочитував би чужі записи.
        auto buffer = std::make_unique<char[]>(BufferSize);
        while (true) {
            long nread = ::syscall(SYS_getdents64, dir_fd, buffer.get(), BufferSize);
            if (nread <= 0) {
                break;
            }

            std::size_t bpos = 0;
            while (bpos < static_cast<std::size_t>(nread)) {
                auto* d = reinterpret_cast<const linux_dirent64*>(buffer.get() + bpos);
                std::string_view name(d->d_name);

                if (name != "." && name != "..") {
                    std::uint8_t dtype = d->d_type;

                    if (dtype == 0 /* DT_UNKNOWN */) {
                        struct stat st{};
                        if (::fstatat(dir_fd, d->d_name, &st, AT_SYMLINK_NOFOLLOW) == 0) {
                            if (S_ISDIR(st.st_mode)) dtype = 4;
                            else if (S_ISREG(st.st_mode)) dtype = 8;
                        }
                    }

                    if (dtype == 4 /* DT_DIR */) {
                        stats_.dirs_count++;
                        ScopedFd child_fd(::openat(dir_fd, d->d_name, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC));
                        if (child_fd.valid()) {
                            process_fd(child_fd.get());
                        }
                    } else if (dtype == 8 /* DT_REG */) {
                        stats_.files_count++;
                    }
                }

                bpos += d->d_reclen;
            }
        }
    }

    TraversalStats stats_{};
};

} // namespace fs_walker

int main(int argc, char* argv[]) {
    std::string path = (argc > 1) ? argv[1] : ".";
    auto result = fs_walker::DirectoryWalker::walk(path);

    if (!result) {
        std::cerr << "Помилка обходу: " << result.error().message() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "Успішно оброблено. Каталогів: " << result->dirs_count 
              << ", файлів: " << result->files_count << '\n';
    return EXIT_SUCCESS;
}
