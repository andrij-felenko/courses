#include <unistd.h>
#include <cstdint>
#include <span>
#include <expected>
#include <system_error>

class ThreadSafeFileWriter {
public:
    static std::expected<size_t, std::error_code> writeChunk(
        int fileDescriptor,
        std::span<const std::byte> data,
        uint64_t fileOffset) noexcept
    {
        off_t currentOffset = static_cast<off_t>(fileOffset);
        const auto* ptr = data.data();
        size_t remaining = data.size();

        while (remaining > 0) {
            ssize_t written = ::pwrite(fileDescriptor, ptr, remaining, currentOffset);
            if (written <= 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            remaining -= static_cast<size_t>(written);
            currentOffset += static_cast<off_t>(written);
            ptr += written;
        }
        return data.size();
    }
};
