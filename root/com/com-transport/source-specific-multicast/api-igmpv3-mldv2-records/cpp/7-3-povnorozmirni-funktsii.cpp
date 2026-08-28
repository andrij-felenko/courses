#include <netinet/in.h>
#include <span>
#include <vector>
#include <expected>
#include <system_error>

/* Безпечна C++ обгортка з використанням std::span та std::expected */
enum class FilterMode : uint32_t { Include = 1, Exclude = 2 };

inline std::expected<void, std::error_code> apply_source_filter(
    int socket_fd, in_addr iface, in_addr group, FilterMode mode, std::span<const in_addr> sources) noexcept {
    if (::setipv4sourcefilter(socket_fd, iface, group, static_cast<uint32_t>(mode),
                              static_cast<uint32_t>(sources.size()), sources.data()) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
