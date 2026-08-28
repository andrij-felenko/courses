#include <span>
#include <cstdint>
#include <bit>
#include <optional>
#include <cstring>

constexpr uint16_t FRAME_MAGIC = 0x4850;
constexpr std::size_t HEADER_SIZE = 8;
constexpr std::size_t TRAILER_SIZE = 4;

struct FrameHeader {
    uint16_t magic;
    uint8_t  version;
    uint8_t  flags;
    uint32_t payload_len;
};

struct ParsedFrame {
    FrameHeader header;
    std::span<const std::byte> payload; // Безволодісний зріз корисного навантаження
    uint32_t crc32;
};

// Ідіоматичний парсер C++20: нуль-копіювання через std::span
std::optional<ParsedFrame> parse_frame_cpp(std::span<const std::byte> buffer) noexcept {
    // 1. Перевірка мінімальної довжини для заголовка та контрольної суми
    if (buffer.size() < HEADER_SIZE + TRAILER_SIZE) {
        return std::nullopt;
    }

    // 2. Вирізаємо статичний зріз заголовка 8 байтів за O(1)
    auto header_bytes = buffer.first<HEADER_SIZE>();
    
    FrameHeader hdr;
    std::memcpy(&hdr, header_bytes.data(), sizeof(FrameHeader));
    
    // Свап байтів для мережевого порядку (big-endian)
    if constexpr (std::endian::native == std::endian::little) {
        hdr.magic = std::byteswap(hdr.magic);
        hdr.payload_len = std::byteswap(hdr.payload_len);
    }

    if (hdr.magic != FRAME_MAGIC || hdr.version != 1) {
        return std::nullopt;
    }

    // 3. Перевірка загального розміру пакета
    const std::size_t total_expected = HEADER_SIZE + hdr.payload_len + TRAILER_SIZE;
    if (buffer.size() < total_expected) {
        return std::nullopt;
    }

    // 4. Відокремлюємо payload та trailer за допомогою subspan
    std::span<const std::byte> payload_span = buffer.subspan(HEADER_SIZE, hdr.payload_len);
    std::span<const std::byte> trailer_span = buffer.subspan(HEADER_SIZE + hdr.payload_len, TRAILER_SIZE);

    uint32_t raw_crc;
    std::memcpy(&raw_crc, trailer_span.data(), sizeof(uint32_t));
    if constexpr (std::endian::native == std::endian::little) {
        raw_crc = std::byteswap(raw_crc);
    }

    return ParsedFrame{
        .header = hdr,
        .payload = payload_span,
        .crc32 = raw_crc
    };
}
