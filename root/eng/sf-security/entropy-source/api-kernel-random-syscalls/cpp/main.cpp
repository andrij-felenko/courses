#include <sys/random.h>
#include <cstddef>
#include <cstdint>
#include <span>
#include <array>
#include <expected>
#include <system_error>

namespace crypto {

[[nodiscard]] inline std::expected<void, std::error_code> fill_random(std::span<std::byte> buffer) noexcept {
    std::byte* ptr = buffer.data();
    std::size_t remaining = buffer.size();

    while (remaining > 0) {
        ssize_t ret = ::getrandom(ptr, remaining, 0);
        if (ret < 0) {
            if (errno == EINTR) {
                continue;
            }
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        ptr += ret;
        remaining -= static_cast<std::size_t>(ret);
    }
    return {};
}

template <std::size_t N>
[[nodiscard]] inline std::expected<std::array<std::byte, N>, std::error_code> generate_random_bytes() noexcept {
    std::array<std::byte, N> buf{};
    if (auto res = fill_random(std::span<std::byte>(buf)); !res) {
        return std::unexpected(res.error());
    }
    return buf;
}

} // namespace crypto
