#include <cstdint>
#include <vector>
#include <span>

namespace flash {

inline constexpr std::size_t EccWordSize = 32; // 256-бітне слово Flash

[[nodiscard]] std::vector<std::uint8_t> create_ecc_aligned_payload(
    std::span<const std::uint8_t> source_data) {
    if (source_data.empty()) return {};

    const auto remainder = source_data.size() % EccWordSize;
    const auto padding = (remainder == 0) ? 0 : (EccWordSize - remainder);
    const auto total_size = source_data.size() + padding;

    std::vector<std::uint8_t> aligned_buffer;
    aligned_buffer.reserve(total_size);

    // Копіювання корисного навантаження
    aligned_buffer.insert(aligned_buffer.end(), source_data.begin(), source_data.end());

    // Заповнення байтами 0xFF
    aligned_buffer.insert(aligned_buffer.end(), padding, 0xFFU);

    return aligned_buffer;
}

} // namespace flash
