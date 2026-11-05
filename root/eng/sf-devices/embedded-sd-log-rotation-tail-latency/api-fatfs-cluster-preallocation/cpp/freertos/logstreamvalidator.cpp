#include "ff.h"
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>

class LogStreamValidator {
public:
    static constexpr uint16_t kMagic = 0xA55A;

    struct FrameHeader {
        uint16_t magic;
        uint16_t payload_len;
        uint32_t seq_id;
        uint32_t timestamp_ms;
    };

    static uint32_t computeCrc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
            }
        }
        return ~crc;
    }

    static FRESULT scanValidBoundary(FIL& file, uint32_t& valid_offset) noexcept {
        FRESULT fr = f_lseek(&file, 0);
        if (fr != FR_OK) return fr;

        alignas(4) std::array<uint8_t, 1024> buffer{};
        UINT bytes_read = 0;
        valid_offset = 0;

        while (f_read(&file, buffer.data(), buffer.size(), &bytes_read) == FR_OK && bytes_read > 0) {
            std::size_t offset = 0;

            while (offset + sizeof(FrameHeader) + sizeof(uint32_t) <= bytes_read) {
                const auto* hdr = reinterpret_cast<const FrameHeader*>(&buffer[offset]);
                if (hdr->magic != kMagic) {
                    return f_lseek(&file, valid_offset);
                }

                const std::size_t frame_len = sizeof(FrameHeader) + hdr->payload_len + sizeof(uint32_t);
                if (offset + frame_len > bytes_read) {
                    break;
                }

                uint32_t stored_crc = 0;
                std::memcpy(&stored_crc, &buffer[offset + sizeof(FrameHeader) + hdr->payload_len], sizeof(uint32_t));

                auto data_span = std::span<const uint8_t>(&buffer[offset], sizeof(FrameHeader) + hdr->payload_len);
                if (computeCrc32(data_span) != stored_crc) {
                    return f_lseek(&file, valid_offset);
                }

                offset += frame_len;
                valid_offset += frame_len;
            }

            if (bytes_read < buffer.size()) break;
        }

        return f_lseek(&file, valid_offset);
    }
};
