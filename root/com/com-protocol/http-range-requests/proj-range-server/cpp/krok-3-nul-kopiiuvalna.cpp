#include <sys/sendfile.h>
#include <sys/socket.h>
#include <unistd.h>
#include <fcntl.h>
#include <string>
#include <format>
#include <expected>
#include <system_error>

class FileDescriptorWrapper {
    int fd_{-1};
public:
    explicit FileDescriptorWrapper(int fd) noexcept : fd_(fd) {}
    ~FileDescriptorWrapper() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }
    FileDescriptorWrapper(const FileDescriptorWrapper&) = delete;
    FileDescriptorWrapper& operator=(const FileDescriptorWrapper&) = delete;
    FileDescriptorWrapper(FileDescriptorWrapper&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

class ZeroCopyRangeSender {
public:
    static std::expected<size_t, std::error_code> sendRange(
        int clientSocket,
        int fileFd,
        const ByteRange& range,
        uint64_t totalFileSize,
        std::string_view contentType)
    {
        const auto headers = std::format(
            "HTTP/1.1 206 Partial Content\r\n"
            "Accept-Ranges: bytes\r\n"
            "Content-Type: {}\r\n"
            "Content-Range: bytes {}-{}/{}\r\n"
            "Content-Length: {}\r\n"
            "Connection: keep-alive\r\n\r\n",
            contentType,
            range.start,
            range.end,
            totalFileSize,
            range.length()
        );

        if (::write(clientSocket, headers.data(), headers.size()) != static_cast<ssize_t>(headers.size())) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        off_t offset = static_cast<off_t>(range.start);
        size_t remaining = static_cast<size_t>(range.length());
        size_t totalSent = 0;

        while (remaining > 0) {
            ssize_t sent = ::sendfile(clientSocket, fileFd, &offset, remaining);
            if (sent <= 0) {
                if (errno == EAGAIN || errno == EINTR) continue;
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            remaining -= static_cast<size_t>(sent);
            totalSent += static_cast<size_t>(sent);
        }
        return totalSent;
    }
};
