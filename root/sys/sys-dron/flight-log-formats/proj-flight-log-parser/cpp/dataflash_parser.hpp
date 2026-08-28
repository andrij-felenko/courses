// ============================================================================
// dataflash_parser.hpp — Потоковий парсер ArduPilot DataFlash на C++20
// ============================================================================
#pragma once
#include <iostream>
#include <vector>
#include <span>
#include <string>
#include <string_view>
#include <unordered_map>
#include <bit>
#include <cstring>
#include <cstdint>
#include <algorithm>

namespace dataflash {

constexpr uint8_t HEAD1 = 0xA3;
constexpr uint8_t HEAD2 = 0x95;
constexpr uint8_t TYPE_FMT = 0x80;

struct MessageFormat {
    uint8_t type_id{0};
    uint8_t length{0};
    std::string name;
    std::string format;
    std::string columns;
};

class Parser {
public:
    void parse_chunk(std::span<const uint8_t> buffer) {
        size_t offset = 0;
        const size_t total_size = buffer.size();

        while (offset + 3 <= total_size) {
            if (buffer[offset] != HEAD1 || buffer[offset + 1] != HEAD2) {
                ++offset;
                ++sync_errors_;
                continue;
            }

            const uint8_t type = buffer[offset + 2];

            if (type == TYPE_FMT) {
                if (offset + 89 > total_size) break;
                parse_fmt(buffer.subspan(offset + 3, 86));
                offset += 89;
                continue;
            }

            auto it = formats_.find(type);
            if (it != formats_.end()) {
                const auto& fmt = it->second;
                if (offset + fmt.length > total_size) break;
                
                dispatch_message(fmt, buffer.subspan(offset + 3, fmt.length - 3));
                offset += fmt.length;
                ++parsed_messages_;
            } else {
                ++offset;
                ++sync_errors_;
            }
        }
    }

    [[nodiscard]] size_t total_parsed() const noexcept { return parsed_messages_; }
    [[nodiscard]] size_t sync_errors() const noexcept { return sync_errors_; }
    [[nodiscard]] const std::unordered_map<uint8_t, MessageFormat>& formats() const noexcept { return formats_; }

private:
    void parse_fmt(std::span<const uint8_t, 86> payload) {
        MessageFormat fmt;
        fmt.type_id = payload[0];
        fmt.length  = payload[1];
        
        fmt.name = extract_string(payload.subspan(2, 4));
        fmt.format = extract_string(payload.subspan(6, 16));
        fmt.columns = extract_string(payload.subspan(22, 64));

        std::cout << "[FMT] Registered: " << fmt.name 
                  << " (0x" << std::hex << static_cast<int>(fmt.type_id) << std::dec
                  << "), Length: " << static_cast<int>(fmt.length) << "\n";

        formats_[fmt.type_id] = std::move(fmt);
    }

    void dispatch_message(const MessageFormat& fmt, std::span<const uint8_t> payload) {
        if (fmt.name == "ATT" && fmt.format == "Qcccc") {
            const uint64_t time_us = read_le<uint64_t>(payload.data());
            const float roll = read_le<int16_t>(payload.data() + 10) / 100.0f;
            const float pitch = read_le<int16_t>(payload.data() + 14) / 100.0f;
            std::cout << "  [ATT] t=" << time_us << " us, Roll=" << roll << " deg, Pitch=" << pitch << " deg\n";
        } else if (fmt.name == "GPS") {
            const uint64_t time_us = read_le<uint64_t>(payload.data());
            const uint8_t status = payload[8];
            const int32_t lat = read_le<int32_t>(payload.data() + 16);
            const int32_t lng = read_le<int32_t>(payload.data() + 20);
            const float alt = read_le<float>(payload.data() + 24);
            std::cout << "  [GPS] t=" << time_us << " us, Status=" << static_cast<int>(status)
                      << ", Pos=(" << (lat / 1e7) << ", " << (lng / 1e7) << "), Alt=" << alt << " m\n";
        }
    }

    static std::string extract_string(std::span<const uint8_t> span) {
        std::string s;
        for (uint8_t b : span) {
            if (b == '\0') break;
            s.push_back(static_cast<char>(b));
        }
        return s;
    }

    template <typename T>
    static T read_le(const uint8_t* ptr) noexcept {
        T val;
        std::memcpy(&val, ptr, sizeof(T));
        if constexpr (std::endian::native == std::endian::big) {
            // Реверс байтів для Big-Endian платформ
            uint8_t* byte_ptr = reinterpret_cast<uint8_t*>(&val);
            std::reverse(byte_ptr, byte_ptr + sizeof(T));
        }
        return val;
    }

    std::unordered_map<uint8_t, MessageFormat> formats_;
    size_t parsed_messages_{0};
    size_t sync_errors_{0};
};

} // namespace dataflash
