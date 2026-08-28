#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <span>
#include <cstdint>
#include <cstring>
#include <algorithm>

// ═════════════════════════════════════════════════════════════════════════════
// 1. БРОКЕР SERVER-SENT EVENTS (SSE) З КІЛЬЦЕВИМ БУФЕРОМ
// ═════════════════════════════════════════════════════════════════════════════

struct SseEvent {
    uint64_t id{0};
    std::string event_type;
    std::string data;

    // Форматування події у канонічний текстовий формат SSE
    [[nodiscard]] std::string serialize() const {
        std::string out;
        out.reserve(data.size() + event_type.size() + 64);
        out += "id: " + std::to_string(id) + "\n";
        if (!event_type.empty()) {
            out += "event: " + event_type + "\n";
        }
        out += "data: " + data + "\n\n";
        return out;
    }
};

class SseRingBuffer {
public:
    explicit SseRingBuffer(size_t capacity)
        : capacity_(capacity), buffer_(capacity), head_(0), count_(0), next_id_(1) {}

    // Додавання нової події до кільцевого буфера
    uint64_t push_event(std::string_view event_type, std::string_view data) {
        uint64_t current_id = next_id_++;
        size_t index = (head_ + count_) % capacity_;

        buffer_[index] = SseEvent{
            .id = current_id,
            .event_type = std::string(event_type),
            .data = std::string(data)
        };

        if (count_ < capacity_) {
            count_++;
        } else {
            head_ = (head_ + 1) % capacity_; // Витіснення найстарішої події
        }
        return current_id;
    }

    // Отримання пропущених подій після last_seen_id
    [[nodiscard]] std::vector<SseEvent> get_events_since(uint64_t last_seen_id) const {
        std::vector<SseEvent> missed;
        if (count_ == 0) return missed;

        uint64_t oldest_id = buffer_[head_].id;
        uint64_t newest_id = buffer_[(head_ + count_ - 1) % capacity_].id;

        // Якщо клієнт уже бачив найновіше
        if (last_seen_id >= newest_id) return missed;

        // Визначаємо зміщення старту досилки
        size_t start_offset = 0;
        if (last_seen_id >= oldest_id) {
            start_offset = static_cast<size_t>(last_seen_id - oldest_id + 1);
        }

        for (size_t i = start_offset; i < count_; ++i) {
            missed.push_back(buffer_[(head_ + i) % capacity_]);
        }
        return missed;
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] uint64_t newest_id() const noexcept { return next_id_ - 1; }

private:
    size_t capacity_;
    std::vector<SseEvent> buffer_;
    size_t head_;
    size_t count_;
    uint64_t next_id_;
};

// ═════════════════════════════════════════════════════════════════════════════
// 2. ДЕКОДЕР ТА ЕНКОДЕР КАДРІВ WEBSOCKET (RFC 6455)
// ═════════════════════════════════════════════════════════════════════════════

enum class WsOpcode : uint8_t {
    Continuation = 0x0,
    Text         = 0x1,
    Binary       = 0x2,
    Close        = 0x8,
    Ping         = 0x9,
    Pong         = 0xA
};

struct WsFrame {
    bool fin{false};
    WsOpcode opcode{WsOpcode::Text};
    bool masked{false};
    std::vector<uint8_t> payload;
};

class WsFrameParser {
public:
    enum class ParseStatus {
        Ok,
        NeedMoreData,
        ProtocolError
    };

    // Розбір сирого буфера байтів
    static std::pair<ParseStatus, std::optional<WsFrame>> parse(
        std::span<const uint8_t> input, size_t& bytes_consumed
    ) {
        bytes_consumed = 0;
        if (input.size() < 2) {
            return {ParseStatus::NeedMoreData, std::nullopt};
        }

        uint8_t byte0 = input[0];
        uint8_t byte1 = input[1];

        bool fin = (byte0 & 0x80) != 0;
        uint8_t rsv = (byte0 & 0x70) >> 4;
        if (rsv != 0) {
            // RSV біти не узгоджені — критична помилка протоколу
            return {ParseStatus::ProtocolError, std::nullopt};
        }

        auto opcode = static_cast<WsOpcode>(byte0 & 0x0F);
        bool masked = (byte1 & 0x80) != 0;
        uint64_t payload_len = byte1 & 0x7F;

        size_t header_len = 2;

        if (payload_len == 126) {
            if (input.size() < header_len + 2) {
                return {ParseStatus::NeedMoreData, std::nullopt};
            }
            payload_len = (static_cast<uint64_t>(input[2]) << 8) | input[3];
            header_len += 2;
        } else if (payload_len == 127) {
            if (input.size() < header_len + 8) {
                return {ParseStatus::NeedMoreData, std::nullopt};
            }
            payload_len = 0;
            for (size_t i = 0; i < 8; ++i) {
                payload_len = (payload_len << 8) | input[header_len + i];
            }
            header_len += 8;
        }

        uint8_t mask_key[4] = {0};
        if (masked) {
            if (input.size() < header_len + 4) {
                return {ParseStatus::NeedMoreData, std::nullopt};
            }
            std::memcpy(mask_key, input.data() + header_len, 4);
            header_len += 4;
        }

        if (input.size() < header_len + payload_len) {
            return {ParseStatus::NeedMoreData, std::nullopt};
        }

        WsFrame frame;
        frame.fin = fin;
        frame.opcode = opcode;
        frame.masked = masked;
        frame.payload.resize(payload_len);

        const uint8_t* payload_src = input.data() + header_len;
        for (size_t i = 0; i < payload_len; ++i) {
            if (masked) {
                frame.payload[i] = payload_src[i] ^ mask_key[i % 4];
            } else {
                frame.payload[i] = payload_src[i];
            }
        }

        bytes_consumed = header_len + payload_len;
        return {ParseStatus::Ok, frame};
    }

    // Складання серверного кадру (завжди без маски)
    static std::vector<uint8_t> build_server_frame(
        WsOpcode opcode, std::span<const uint8_t> payload, bool fin = true
    ) {
        std::vector<uint8_t> out;
        uint8_t byte0 = (fin ? 0x80 : 0x00) | (static_cast<uint8_t>(opcode) & 0x0F);
        out.push_back(byte0);

        size_t len = payload.size();
        if (len <= 125) {
            out.push_back(static_cast<uint8_t>(len)); // MASK = 0
        } else if (len <= 0xFFFF) {
            out.push_back(126);
            out.push_back(static_cast<uint8_t>((len >> 8) & 0xFF));
            out.push_back(static_cast<uint8_t>(len & 0xFF));
        } else {
            out.push_back(127);
            for (int i = 7; i >= 0; --i) {
                out.push_back(static_cast<uint8_t>((len >> (i * 8)) & 0xFF));
            }
        }

        out.insert(out.end(), payload.begin(), payload.end());
        return out;
    }
};
