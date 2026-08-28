#include <sys/stat.h>
#include <fcntl.h>
#include <iostream>

void handleHttpGet(
    int clientSocket,
    const std::string& filePath,
    std::string_view rangeHeader,
    std::string_view ifRangeHeader)
{
    int rawFd = ::open(filePath.c_str(), O_RDONLY);
    if (rawFd < 0) {
        constexpr std::string_view k404 = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n";
        ::write(clientSocket, k404.data(), k404.size());
        return;
    }
    FileDescriptorWrapper file(rawFd);

    struct stat st{};
    if (::fstat(file.get(), &st) < 0) return;
    uint64_t fileSize = static_cast<uint64_t>(st.st_size);

    constexpr std::string_view kEtag = "\"a98c7e-524\"";
    constexpr std::string_view kLastMod = "Wed, 20 Aug 2026 10:00:00 GMT";

    bool canServePartial = IfRangeValidator::isSatisfied(ifRangeHeader, kEtag, kLastMod);

    if (!rangeHeader.empty() && canServePartial) {
        auto parsed = RangeParser::parse(rangeHeader, fileSize);
        if (parsed.unsatisfiable) {
            const auto err416 = std::format(
                "HTTP/1.1 416 Range Not Satisfiable\r\n"
                "Content-Range: bytes */{}\r\n"
                "Content-Length: 0\r\n\r\n", fileSize);
            ::write(clientSocket, err416.data(), err416.size());
            return;
        }

        if (parsed.ranges.size() == 1) {
            auto res = ZeroCopyRangeSender::sendRange(
                clientSocket, file.get(), parsed.ranges.front(), fileSize, "video/mp4");
            if (!res) {
                std::cerr << "Помилка передачі зрізу: " << res.error().message() << '\n';
            }
            return;
        } else if (parsed.ranges.size() > 1) {
            auto res = MultipartRangeSender::sendMultipart(
                clientSocket, file.get(), parsed.ranges, fileSize, "video/mp4");
            if (!res) {
                std::cerr << "Помилка передачі multipart: " << res.error().message() << '\n';
            }
            return;
        }
    }

    // Fallback: 200 OK повний файл
    const auto ok200 = std::format(
        "HTTP/1.1 200 OK\r\n"
        "Accept-Ranges: bytes\r\n"
        "ETag: {}\r\n"
        "Last-Modified: {}\r\n"
        "Content-Length: {}\r\n"
        "Content-Type: video/mp4\r\n\r\n",
        kEtag, kLastMod, fileSize);
    ::write(clientSocket, ok200.data(), ok200.size());

    off_t offset = 0;
    size_t rem = fileSize;
    while (rem > 0) {
        ssize_t s = ::sendfile(clientSocket, file.get(), &offset, rem);
        if (s <= 0) break;
        rem -= static_cast<size_t>(s);
    }
}
