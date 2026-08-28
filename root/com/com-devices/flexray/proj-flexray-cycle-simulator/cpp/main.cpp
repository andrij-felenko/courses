#include <iostream>
#include <vector>
#include <array>
#include <cstdint>
#include <span>
#include <expected>
#include <iomanip>

class FlexRayFrame {
public:
    static constexpr uint16_t HEADER_CRC_POLY = 0x385;
    static constexpr uint32_t FRAME_CRC_POLY  = 0x5B2EC7;

    struct Header {
        bool     payload_preamble{false};
        bool     null_frame{true};
        bool     sync_frame{false};
        bool     startup_frame{false};
        uint16_t frame_id{1};       // 1 .. 2047
        uint16_t payload_length{0}; // в 16-бітних словах (0 .. 127)
        uint16_t header_crc{0};     // 11-бітний CRC
        uint8_t  cycle_count{0};    // 0 .. 63
    };

    enum class FrameError {
        InvalidPayloadSize,
        InvalidHeaderCRC,
        InvalidFrameCRC
    };

    explicit FlexRayFrame(Header header, std::span<const uint16_t> data_words)
        : header_(header) {
        payload_.resize(data_words.size() * 2);
        for (size_t i = 0; i < data_words.size(); ++i) {
            payload_[i * 2]     = static_cast<uint8_t>(data_words[i] >> 8);
            payload_[i * 2 + 1] = static_cast<uint8_t>(data_words[i] & 0xFF);
        }
        header_.payload_length = static_cast<uint16_t>(data_words.size());
        header_.header_crc = compute_header_crc();
        frame_crc_ = compute_frame_crc();
    }

    [[nodiscard]] uint16_t compute_header_crc() const noexcept {
        uint32_t crc = 0x01A;
        uint32_t data_word = 0;
        data_word |= (static_cast<uint32_t>(header_.sync_frame) & 0x01) << 19;
        data_word |= (static_cast<uint32_t>(header_.startup_frame) & 0x01) << 18;
        data_word |= (static_cast<uint32_t>(header_.frame_id) & 0x7FF) << 7;
        data_word |= (static_cast<uint32_t>(header_.payload_length) & 0x7F);

        for (int i = 19; i >= 0; --i) {
            uint32_t bit = (data_word >> i) & 0x01;
            uint32_t crc_msb = (crc >> 10) & 0x01;
            crc = (crc << 1) & 0x7FF;
            if (bit ^ crc_msb) {
                crc ^= HEADER_CRC_POLY;
            }
        }
        return static_cast<uint16_t>(crc & 0x7FF);
    }

    [[nodiscard]] uint32_t compute_frame_crc() const noexcept {
        uint32_t crc = 0xFEDCBA;

        std::array<uint8_t, 5> header_bytes{};
        header_bytes[0] = (header_.payload_preamble << 6) |
                          (header_.null_frame << 5) |
                          (header_.sync_frame << 4) |
                          (header_.startup_frame << 3) |
                          ((header_.frame_id >> 8) & 0x07);
        header_bytes[1] = header_.frame_id & 0xFF;
        header_bytes[2] = ((header_.payload_length >> 4) & 0x0F) |
                          ((header_.header_crc >> 7) & 0xF0);
        header_bytes[3] = (header_.header_crc << 1) & 0xFE;
        header_bytes[4] = header_.cycle_count & 0x3F;

        auto process_byte = [&crc](uint8_t byte) {
            for (int i = 7; i >= 0; --i) {
                uint32_t bit = (byte >> i) & 0x01;
                uint32_t crc_msb = (crc >> 23) & 0x01;
                crc = (crc << 1) & 0xFFFFFF;
                if (bit ^ crc_msb) {
                    crc ^= FRAME_CRC_POLY;
                }
            }
        };

        for (uint8_t b : header_bytes) {
            process_byte(b);
        }
        for (uint8_t b : payload_) {
            process_byte(b);
        }
        return crc & 0xFFFFFF;
    }

    [[nodiscard]] std::expected<void, FrameError> verify() const noexcept {
        if (compute_header_crc() != header_.header_crc) {
            return std::unexpected(FrameError::InvalidHeaderCRC);
        }
        if (compute_frame_crc() != frame_crc_) {
            return std::unexpected(FrameError::InvalidFrameCRC);
        }
        return {};
    }

    [[nodiscard]] Header header() const noexcept { return header_; }
    [[nodiscard]] uint32_t frame_crc() const noexcept { return frame_crc_; }
    [[nodiscard]] std::span<const uint8_t> payload() const noexcept { return payload_; }

private:
    Header header_;
    std::vector<uint8_t> payload_;
    uint32_t frame_crc_{0};
};

int main() {
    FlexRayFrame::Header hdr{
        .payload_preamble = false,
        .null_frame       = true,
        .sync_frame       = true,
        .startup_frame    = false,
        .frame_id         = 12,
        .cycle_count      = 1
    };

    const std::array<uint16_t, 4> data{ 0x1234, 0x5678, 0x9ABC, 0xDEF0 };
    FlexRayFrame frame(hdr, data);

    std::cout << "FlexRay Frame Simulator (C++20 Modern Execution):\n";
    std::cout << "-------------------------------------------------\n";
    std::cout << "Frame ID:       " << frame.header().frame_id << " (Static Slot)\n";
    std::cout << "Payload Length: " << static_cast<int>(frame.header().payload_length) << " words\n";
    std::cout << "Header CRC:     0x" << std::hex << std::uppercase << frame.header().header_crc << "\n";
    std::cout << "Frame CRC:      0x" << frame.frame_crc() << std::dec << "\n";

    auto result = frame.verify();
    if (result.has_value()) {
        std::cout << "Verification:   PASSED (OK)\n";
    } else {
        std::cout << "Verification:   FAILED\n";
    }

    return 0;
}
