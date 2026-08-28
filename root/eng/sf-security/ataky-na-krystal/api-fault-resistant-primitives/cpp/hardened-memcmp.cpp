#include <cstdint>
#include <cstddef>
#include <span>

namespace sec {

[[nodiscard]] Token constant_time_compare(std::span<const std::uint8_t> a,
                                          std::span<const std::uint8_t> b) noexcept;

} // namespace sec
