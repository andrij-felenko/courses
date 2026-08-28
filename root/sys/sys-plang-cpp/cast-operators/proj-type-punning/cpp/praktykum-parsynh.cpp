#include <cstdint>
#include <cstring>
#include <span>
#include <optional>
#include <string_view>

struct WavHeader {
    uint32_t riff_size{};
    uint32_t sample_rate{};
    uint32_t byte_rate{};
    uint32_t data_size{};
    uint16_t audio_format{};
    uint16_t num_channels{};
    uint16_t block_align{};
    uint16_t bits_per_sample{};
};

std::optional<WavHeader> parse_wav_stream(std::span<const std::byte> bytes) noexcept {
    constexpr size_t kWavHeaderSize = 44;
    if (bytes.size() < kWavHeaderSize) {
        return std::nullopt;
    }

    // Перевірка сигнатур "RIFF" та "WAVE"
    const auto* data = reinterpret_cast<const char*>(bytes.data());
    if (std::string_view(data, 4) != "RIFF" || std::string_view(data + 8, 4) != "WAVE") {
        return std::nullopt;
    }

    WavHeader hdr{};
    // Побайтове копіювання окремих полів з точними зміщеннями специфікації RIFF
    std::memcpy(&hdr.riff_size,       bytes.data() + 4,  sizeof(uint32_t));
    std::memcpy(&hdr.audio_format,    bytes.data() + 20, sizeof(uint16_t));
    std::memcpy(&hdr.num_channels,    bytes.data() + 22, sizeof(uint16_t));
    std::memcpy(&hdr.sample_rate,     bytes.data() + 24, sizeof(uint32_t));
    std::memcpy(&hdr.byte_rate,       bytes.data() + 28, sizeof(uint32_t));
    std::memcpy(&hdr.block_align,     bytes.data() + 32, sizeof(uint16_t));
    std::memcpy(&hdr.bits_per_sample, bytes.data() + 34, sizeof(uint16_t));
    std::memcpy(&hdr.data_size,       bytes.data() + 40, sizeof(uint32_t));

    return hdr;
}
