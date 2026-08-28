// ============================================================================
// ulog_parser.hpp — Потоковий парсер PX4 ULog на C++20
// ============================================================================
#pragma once
#include <iostream>
#include <vector>
#include <span>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <cstring>
#include <cstdint>

namespace ulog {

struct FormatDefinition {
    std::string name;
    std::string raw_schema;
};

struct Subscription {
    uint16_t msg_id{0};
    uint8_t multi_id{0};
    std::string topic_name;
    std::shared_ptr<FormatDefinition> format;
};

class Parser {
public:
    void parse_chunk(std::span<const uint8_t> buffer) {
        size_t offset = 0;
        const size_t total_size = buffer.size();

        if (!header_verified_) {
            if (total_size < 16) return;
            if (!verify_header(buffer.subspan(0, 16))) return;
            offset = 16;
            header_verified_ = true;
        }

        while (offset + 3 <= total_size) {
            const uint16_t msg_size = buffer[offset] | (static_cast<uint16_t>(buffer[offset + 1]) << 8);
            const uint8_t msg_type = buffer[offset + 2];

            if (offset + 3 + msg_size > total_size) break;

            auto payload = buffer.subspan(offset + 3, msg_size);
            dispatch_section(msg_type, payload);
            offset += 3 + msg_size;
        }
    }

    [[nodiscard]] size_t total_data_samples() const noexcept { return data_messages_; }
    [[nodiscard]] size_t total_dropouts() const noexcept { return dropouts_; }

private:
    bool verify_header(std::span<const uint8_t, 16> hdr) {
        constexpr uint8_t expected_magic[7] = {0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35};
        if (std::memcmp(hdr.data(), expected_magic, 7) != 0) {
            std::cerr << "Помилка: недійсний магічний заголовок ULog!\n";
            return false;
        }
        std::memcpy(&start_time_us_, hdr.data() + 7, sizeof(uint64_t));
        std::cout << "[ULOG] Валідний файл ULog. Час старту: " << start_time_us_ << " мкс\n";
        return true;
    }

    void dispatch_section(uint8_t type, std::span<const uint8_t> payload) {
        switch (type) {
            case 'F': {
                std::string_view schema(reinterpret_cast<const char*>(payload.data()), payload.size());
                auto colon = schema.find(':');
                if (colon != std::string_view::npos) {
                    auto name = std::string(schema.substr(0, colon));
                    auto fmt = std::make_shared<FormatDefinition>(name, std::string(schema));
                    formats_[name] = fmt;
                    std::cout << "[ULOG-F] Зареєстровано формат: " << name << "\n";
                }
                break;
            }
            case 'A': {
                if (payload.size() < 3) break;
                const uint8_t multi_id = payload[0];
                const uint16_t msg_id = payload[1] | (static_cast<uint16_t>(payload[2]) << 8);
                std::string topic_name(reinterpret_cast<const char*>(payload.data() + 3), payload.size() - 3);

                Subscription sub{msg_id, multi_id, topic_name, nullptr};
                auto it = formats_.find(topic_name);
                if (it != formats_.end()) {
                    sub.format = it->second;
                }
                subscriptions_[msg_id] = sub;
                std::cout << "[ULOG-A] ID " << msg_id << " -> " << topic_name << " (inst " << static_cast<int>(multi_id) << ")\n";
                break;
            }
            case 'D': {
                if (payload.size() >= 2) {
                    ++data_messages_;
                }
                break;
            }
            case 'L': {
                if (payload.size() >= 9) {
                    const uint8_t level = payload[0];
                    uint64_t ts;
                    std::memcpy(&ts, payload.data() + 1, sizeof(uint64_t));
                    std::string_view text(reinterpret_cast<const char*>(payload.data() + 9), payload.size() - 9);
                    std::cout << "  [LOG L" << static_cast<int>(level) << "] t=" << ts << " us: " << text << "\n";
                }
                break;
            }
            case 'S': {
                if (payload.size() >= 2) {
                    const uint16_t duration_ms = payload[0] | (static_cast<uint16_t>(payload[1]) << 8);
                    ++dropouts_;
                    std::cout << "  [ULOG-S] Фіксація пропуску даних: " << duration_ms << " мс\n";
                }
                break;
            }
            default:
                break;
        }
    }

    bool header_verified_{false};
    uint64_t start_time_us_{0};
    std::unordered_map<std::string, std::shared_ptr<FormatDefinition>> formats_;
    std::unordered_map<uint16_t, Subscription> subscriptions_;
    size_t data_messages_{0};
    size_t dropouts_{0};
};

} // namespace ulog
