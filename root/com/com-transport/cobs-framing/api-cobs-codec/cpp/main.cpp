#include <cstddef>

namespace cobs {

/**
 * Константний вираз часу компіляції для максимального розміру закодованого буфера.
 */
[[nodiscard]] constexpr size_t encoded_max_size(size_t payload_size) noexcept {
    return payload_size + (payload_size / 254) + 1 + 1;
}

/**
 * Константний вираз для максимального розміру відновленого корисного навантаження.
 */
[[nodiscard]] constexpr size_t decoded_max_size(size_t encoded_size) noexcept {
    return (encoded_size > 1) ? (encoded_size - 1) : 0;
}

} // namespace cobs
