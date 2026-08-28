#include <iostream>
#include <system_error>
#include <expected>
#include <span>
#include <vector>
#include <memory>
#include <optional>
#include <cerrno>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/fs.h>

#ifndef FICLONE
#define FICLONE _IOW(0x94, 9, int)
#endif

namespace sysio {

// RAII Обгортка для файлового дескриптора
class UniqueFd {
    int m_fd{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : m_fd(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset();
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        m_fd = new_fd;
    }
};

// Ідіоматичний клонер C++23 з використанням std::expected
class FileCloner {
    static constexpr size_t ChunkBufferSizeBytes = 256 * 1024;

public:
    static std::expected<size_t, std::error_code> clone_file(
        int fd_in, std::optional<loff_t> off_in,
        int fd_out, std::optional<loff_t> off_out,
        size_t len) noexcept
    {
        loff_t pos_in = off_in.value_or(0);
        loff_t pos_out = off_out.value_or(0);
        loff_t* p_in = off_in.has_value() ? &pos_in : nullptr;
        loff_t* p_out = off_out.has_value() ? &pos_out : nullptr;

        // 1. Спроба Reflink FICLONE
        if (!off_in.has_value() && !off_out.has_value() && len == 0) {
            if (::ioctl(fd_out, FICLONE, fd_in) == 0) {
                struct stat st{};                 // склоновано весь файл — повертаємо
                if (::fstat(fd_in, &st) != 0) {   // його розмір, бо 0 означає EOF
                    return std::unexpected(std::error_code(errno, std::generic_category()));
                }
                return static_cast<size_t>(st.st_size);
            }
            if (errno != EXDEV && errno != EOPNOTSUPP && errno != ENOTTY && errno != EINVAL) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
        }

        // 2. Спроба copy_file_range
        size_t total_copied = 0;
        size_t remaining = len;

        while (remaining > 0 || len == 0) {
            size_t request_size = (len == 0) ? (1024 * 1024 * 1024) : remaining;
            ssize_t ret = ::copy_file_range(fd_in, p_in, fd_out, p_out, request_size, 0);

            if (ret > 0) {
                total_copied += static_cast<size_t>(ret);
                if (len > 0) remaining -= static_cast<size_t>(ret);
                continue;
            }

            if (ret == 0) break; // EOF

            if (errno == EINTR) continue;

            if (errno == EXDEV || errno == EOPNOTSUPP || errno == ENOSYS || errno == EINVAL) {
                break; // Каскадний перехід до splice
            }

            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (total_copied > 0 || (len > 0 && remaining == 0)) {
            return total_copied;
        }

        // 3. Splice Zero-Copy Fallback
        int pipe_fds[2];
        if (::pipe2(pipe_fds, O_CLOEXEC | O_NONBLOCK) == 0) {
            UniqueFd pipe_read(pipe_fds[0]);
            UniqueFd pipe_write(pipe_fds[1]);

            ::fcntl(pipe_write.get(), F_SETPIPE_SZ, 1024 * 1024);

            while (remaining > 0 || len == 0) {
                size_t req = (len == 0 || remaining > ChunkBufferSizeBytes) ? ChunkBufferSizeBytes : remaining;
                ssize_t s_in = ::splice(fd_in, p_in, pipe_write.get(), nullptr, req, SPLICE_F_MOVE | SPLICE_F_MORE);

                if (s_in > 0) {
                    ssize_t s_out = ::splice(pipe_read.get(), nullptr, fd_out, p_out, static_cast<size_t>(s_in), SPLICE_F_MOVE);
                    if (s_out > 0) {
                        total_copied += static_cast<size_t>(s_out);
                        if (len > 0) remaining -= static_cast<size_t>(s_out);
                        continue;
                    }
                }

                if (s_in == 0) break; // EOF
                if (errno == EINTR) continue;

                break;
            }
        }

        if (total_copied > 0 || (len > 0 && remaining == 0)) {
            return total_copied;
        }

        // 4. POSIX pread/pwrite fallback
        std::vector<char> buffer(ChunkBufferSizeBytes);
        ::posix_fadvise(fd_in, p_in ? *p_in : 0, remaining, POSIX_FADV_SEQUENTIAL);

        while (remaining > 0 || len == 0) {
            size_t req = (len == 0 || remaining > ChunkBufferSizeBytes) ? ChunkBufferSizeBytes : remaining;
            ssize_t r_bytes = p_in ? ::pread(fd_in, buffer.data(), req, *p_in)
                                   : ::read(fd_in, buffer.data(), req);

            if (r_bytes > 0) {
                if (p_in) *p_in += r_bytes;
                ssize_t w_bytes = p_out ? ::pwrite(fd_out, buffer.data(), static_cast<size_t>(r_bytes), *p_out)
                                        : ::write(fd_out, buffer.data(), static_cast<size_t>(r_bytes));

                if (w_bytes > 0) {
                    if (p_out) *p_out += w_bytes;
                    total_copied += static_cast<size_t>(w_bytes);
                    if (len > 0) remaining -= static_cast<size_t>(w_bytes);
                    continue;
                }
            }

            if (r_bytes == 0) break; // EOF
            if (errno == EINTR) continue;

            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return total_copied;
    }
};

} // namespace sysio
