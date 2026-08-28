#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <cstdint>
#include <system_error>
#include <expected>
#include <vector>
#include <array>
#include <span>
#include <utility>

#ifndef FICLONE
#define FICLONE _IOW(0x94, 9, int)
#endif

// RAII обгортка для файлового дескриптора Linux
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
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
        return std::exchange(fd_, -1);
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

// Промисловий рушій копіювання мовою C++23 з використанням std::expected
class FileCopyEngine {
public:
    static constexpr size_t BufferSize = 64 * 1024;

    static std::expected<uint64_t, std::error_code> copy(int fd_in, int fd_out, uint64_t bytes_to_copy) {
        uint64_t total_copied = 0;
        bool try_copy_file_range = true;

        // Підказка ядру про послідовне зчитування
        ::posix_fadvise(fd_in, 0, static_cast<off_t>(bytes_to_copy), POSIX_FADV_SEQUENTIAL);

        // Спроба миттєвого Reflink через ioctl(FICLONE) якщо обсяг дорівнює 0 (весь файл)
        if (bytes_to_copy == 0) {
            struct stat st{};
            if (::fstat(fd_in, &st) == 0 && S_ISREG(st.st_mode)) {
                if (::ioctl(fd_out, FICLONE, fd_in) == 0) {
                    return static_cast<uint64_t>(st.st_size);
                }
                // Клон не вдався — копіюємо весь файл звичайним шляхом
                bytes_to_copy = static_cast<uint64_t>(st.st_size);
            }
            if (bytes_to_copy == 0) {
                return 0ULL;
            }
        }

        while (total_copied < bytes_to_copy) {
            const size_t chunk = static_cast<size_t>(
                std::min<uint64_t>(bytes_to_copy - total_copied, 1073741824ULL) // 1 ГіБ максимум за крок
            );

            if (try_copy_file_range) {
                ssize_t ret = ::copy_file_range(fd_in, nullptr, fd_out, nullptr, chunk, 0);

                if (ret > 0) {
                    total_copied += static_cast<uint64_t>(ret);
                    continue;
                }

                if (ret == 0) {
                    break; // Досягнуто EOF
                }

                int err = errno;
                if (err == EINTR) {
                    continue;
                }

                struct stat si{}, so{};
                const bool same_inode = ::fstat(fd_in, &si) == 0 && ::fstat(fd_out, &so) == 0 &&
                                        si.st_dev == so.st_dev && si.st_ino == so.st_ino;

                // EINVAL на спільному іноді — це перекриття діапазонів;
                // відкат на read/write тут зіпсував би дані
                if (err == EXDEV || err == ENOSYS || err == EOPNOTSUPP ||
                    (err == EINVAL && !same_inode)) {
                    // Фолбек при відсутності підтримки з боку ядра або ФС
                    try_copy_file_range = false;
                    auto fb_res = fallback_read_write(fd_in, fd_out, bytes_to_copy - total_copied);
                    if (!fb_res) {
                        return std::unexpected(fb_res.error());
                    }
                    total_copied += fb_res.value();
                    break;
                }

                return std::unexpected(std::error_code(err, std::generic_category()));
            }
        }

        return total_copied;
    }

private:
    static std::expected<uint64_t, std::error_code> fallback_read_write(int fd_in, int fd_out, uint64_t count) {
        std::array<char, BufferSize> buffer{};
        uint64_t total_written = 0;

        while (total_written < count) {
            const size_t to_read = static_cast<size_t>(
                std::min<uint64_t>(count - total_written, buffer.size())
            );

            ssize_t nread = ::read(fd_in, buffer.data(), to_read);
            if (nread < 0) {
                if (errno == EINTR) continue;
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            if (nread == 0) break; // Досягнуто EOF

            size_t bytes_written_in_chunk = 0;
            while (bytes_written_in_chunk < static_cast<size_t>(nread)) {
                ssize_t nwritten = ::write(
                    fd_out,
                    buffer.data() + bytes_written_in_chunk,
                    static_cast<size_t>(nread) - bytes_written_in_chunk
                );
                if (nwritten < 0) {
                    if (errno == EINTR) continue;
                    return std::unexpected(std::error_code(errno, std::generic_category()));
                }
                bytes_written_in_chunk += static_cast<size_t>(nwritten);
            }
            total_written += static_cast<size_t>(nread);
        }

        return total_written;
    }
};
