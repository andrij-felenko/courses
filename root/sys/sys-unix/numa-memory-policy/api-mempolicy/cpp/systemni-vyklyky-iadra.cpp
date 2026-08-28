#include <numaif.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <cstdint>
#include <span>
#include <expected>
#include <system_error>

namespace numa {

enum class Mode : int {
    Default       = 0,
    Bind          = 1,
    Interleave    = 2,
    Preferred     = 3,
    Local         = 4,
    PreferredMany = 5
};

/* Безпечна C++ обгортка для встановлення політики пам'яті діапазону */
[[nodiscard]] inline std::expected<void, std::error_code> bind_range(
    std::span<std::byte> buffer,
    Mode mode,
    const unsigned long* nodemask,
    unsigned long maxnode,
    unsigned int flags) noexcept
{
    long ret = ::mbind(buffer.data(), buffer.size(),
                       static_cast<int>(mode), nodemask, maxnode, flags);
    if (ret != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace numa
