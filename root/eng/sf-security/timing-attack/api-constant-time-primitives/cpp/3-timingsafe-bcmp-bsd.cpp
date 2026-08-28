#include <string.h>
#include <span>
#include <cstddef>

/* C++ інтерфейс для системного виклику */
[[nodiscard]] bool bsd_safe_compare(std::span<const std::byte> b1, std::span<const std::byte> b2) noexcept {
    if (b1.size() != b2.size()) {
        return false;
    }
    return timingsafe_bcmp(b1.data(), b2.data(), b1.size_bytes()) == 0;
}
