#include <iostream>
#include <vector>
#include <span>
#include <string>
#include <string_view>
#include <unordered_map>
#include <optional>
#include <shared_mutex>
#include <mutex>
#include <cstdint>
#include <stdexcept>

namespace schema_wire {

inline constexpr uint8_t MAGIC_BYTE = 0x00;
inline constexpr size_t HEADER_SIZE = 5;

/* Потокобезпечний кеш схем для гарячого шляху десеріалізації без копіювання */
class ThreadSafeSchemaCache {
public:
    void put(uint32_t schema_id, std::string schema_json) {
        std::unique_lock lock(mutex_);
        cache_[schema_id] = std::move(schema_json);
    }

    [[nodiscard]] std::optional<std::string> get(uint32_t schema_id) const {
        std::shared_lock lock(mutex_);
        if (auto it = cache_.find(schema_id); it != cache_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    [[nodiscard]] size_t size() const {
        std::shared_lock lock(mutex_);
        return cache_.size();
    }

private:
    mutable std::shared_mutex mutex_;
    std::unordered_map<uint32_t, std::string> cache_;
};

/* Серіалізація повідомлення у Confluent Wire Format (std::span) */
[[nodiscard]] std::vector<uint8_t> encode(uint32_t schema_id, std::span<const uint8_t> payload) {
    std::vector<uint8_t> buffer;
    buffer.reserve(HEADER_SIZE + payload.size());

    // Байт 0: Magic byte
    buffer.push_back(MAGIC_BYTE);

    // Байти 1–4: Schema ID у Big-Endian форматі
    buffer.push_back(static_cast<uint8_t>((schema_id >> 24) & 0xFF));
    buffer.push_back(static_cast<uint8_t>((schema_id >> 16) & 0xFF));
    buffer.push_back(static_cast<uint8_t>((schema_id >> 8) & 0xFF));
    buffer.push_back(static_cast<uint8_t>(schema_id & 0xFF));

    // Тіло повідомлення
    buffer.insert(buffer.end(), payload.begin(), payload.end());
    return buffer;
}

struct ParsedFrame {
    uint32_t schema_id;
    std::span<const uint8_t> payload;
};

/* Декодування та витягнення ідентифікатора схеми без додаткового виділення пам'яті */
[[nodiscard]] std::optional<ParsedFrame> decode(std::span<const uint8_t> frame) noexcept {
    if (frame.size() < HEADER_SIZE || frame[0] != MAGIC_BYTE) {
        return std::nullopt;
    }

    uint32_t schema_id = (static_cast<uint32_t>(frame[1]) << 24) |
                         (static_cast<uint32_t>(frame[2]) << 16) |
                         (static_cast<uint32_t>(frame[3]) << 8)  |
                         (static_cast<uint32_t>(frame[4]));

    return ParsedFrame{
        .schema_id = schema_id,
        .payload = frame.subspan(HEADER_SIZE)
    };
}

} // namespace schema_wire
