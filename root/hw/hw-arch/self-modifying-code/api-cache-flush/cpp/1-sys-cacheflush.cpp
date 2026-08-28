#include <unistd.h>
#include <sys/syscall.h>
#include <span>
#include <expected>
#include <system_error>

inline std::expected<void, std::error_code> flush_cache_range(
    std::span<uint8_t> buffer, int operation_flags) noexcept {
    long ret = syscall(__NR_cacheflush, buffer.data(), static_cast<int>(buffer.size()), operation_flags);
    if (ret != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
