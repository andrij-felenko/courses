#include <sys/uio.h>

class MultipartRangeSender {
public:
    static std::expected<void, std::error_code> sendMultipart(
        int clientSocket,
        int fileFd,
        const std::vector<ByteRange>& ranges,
        uint64_t totalFileSize,
        std::string_view contentType)
    {
        constexpr std::string_view kBoundary = "3d92f57df30dec";
        const auto mainHeader = std::format(
            "HTTP/1.1 206 Partial Content\r\n"
            "Accept-Ranges: bytes\r\n"
            "Content-Type: multipart/byteranges; boundary={}\r\n"
            "Connection: keep-alive\r\n\r\n", kBoundary);

        if (::write(clientSocket, mainHeader.data(), mainHeader.size()) != static_cast<ssize_t>(mainHeader.size())) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        for (const auto& range : ranges) {
            const auto partHeader = std::format(
                "--{}\r\n"
                "Content-Type: {}\r\n"
                "Content-Range: bytes {}-{}/{}\r\n\r\n",
                kBoundary, contentType, range.start, range.end, totalFileSize);

            if (::write(clientSocket, partHeader.data(), partHeader.size()) != static_cast<ssize_t>(partHeader.size())) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            off_t offset = static_cast<off_t>(range.start);
            size_t rem = static_cast<size_t>(range.length());
            while (rem > 0) {
                ssize_t sent = ::sendfile(clientSocket, fileFd, &offset, rem);
                if (sent <= 0) {
                    if (errno == EAGAIN || errno == EINTR) continue;
                    return std::unexpected(std::error_code(errno, std::generic_category()));
                }
                rem -= static_cast<size_t>(sent);
            }
            if (::write(clientSocket, "\r\n", 2) != 2) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
        }

        const auto finalBoundary = std::format("--{}--\r\n", kBoundary);
        if (::write(clientSocket, finalBoundary.data(), finalBoundary.size()) != static_cast<ssize_t>(finalBoundary.size())) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }
};
