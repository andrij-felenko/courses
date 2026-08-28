#include <cstdint>
#include <cstddef>
#include <cstring>
#include <array>
#include <span>
#include <optional>
#include <chrono>

namespace embedded::security {

constexpr uint16_t FrameMagic = 0xA55AU;
constexpr size_t TagSize = 32;
constexpr uint64_t ReplayWindowSize = 64;

enum class ParseError {
    BufferTooSmall,
    InvalidMagic,
    PayloadMismatch,
    AuthFailed,
    TimestampExpired,
    ReplayDetected
};

#pragma pack(push, 1)
struct FrameHeader {
    uint16_t magic;
    uint8_t  msg_type;
    uint8_t  reserved;
    uint64_t seq_num;
    uint32_t timestamp;
    uint16_t payload_len;
};
#pragma pack(pop)

struct ValidatedCommand {
    uint8_t msg_type;
    uint64_t seq_num;
    uint32_t timestamp;
    std::span<const uint8_t> payload;
};

class ReplayWindow {
public:
    constexpr ReplayWindow() noexcept : max_seq_(0), bitmap_(0) {}

    [[nodiscard]] bool check(uint64_t seq) const noexcept {
        if (seq == 0) return false;
        if (seq > max_seq_) return true;
        uint64_t diff = max_seq_ - seq;
        if (diff >= ReplayWindowSize) return false;
        return (bitmap_ & (1ULL << diff)) == 0;
    }

    void commit(uint64_t seq) noexcept {
        if (seq > max_seq_) {
            uint64_t shift = seq - max_seq_;
            if (shift >= ReplayWindowSize) {
                bitmap_ = 1ULL;
            } else {
                bitmap_ = (bitmap_ << shift) | 1ULL;
            }
            max_seq_ = seq;
        } else {
            uint64_t diff = max_seq_ - seq;
            if (diff < ReplayWindowSize) {
                bitmap_ |= (1ULL << diff);
            }
        }
    }

    [[nodiscard]] uint64_t max_sequence() const noexcept { return max_seq_; }

private:
    uint64_t max_seq_;
    uint64_t bitmap_;
};

class CommandVerifier {
public:
    using Key = std::span<const uint8_t>;
    using Tag = std::array<uint8_t, TagSize>;

    explicit CommandVerifier(Key symmetric_key) noexcept : key_(symmetric_key) {}

    template <typename ExpectedType = ValidatedCommand>
    struct Result {
        std::optional<ExpectedType> value;
        std::optional<ParseError> error;

        [[nodiscard]] bool has_value() const noexcept { return value.has_value(); }
        [[nodiscard]] const ExpectedType& operator*() const noexcept { return *value; }
        [[nodiscard]] ParseError get_error() const noexcept { return *error; }
    };

    Result<ValidatedCommand> parse(std::span<const uint8_t> frame_bytes,
                                   uint32_t current_time = 0,
                                   uint32_t max_time_drift = 0) noexcept {
        if (frame_bytes.size() < sizeof(FrameHeader) + TagSize) {
            return {std::nullopt, ParseError::BufferTooSmall};
        }

        FrameHeader header;
        std::memcpy(&header, frame_bytes.data(), sizeof(FrameHeader));

        if (header.magic != FrameMagic) {
            return {std::nullopt, ParseError::InvalidMagic};
        }

        size_t expected_len = sizeof(FrameHeader) + header.payload_len + TagSize;
        if (frame_bytes.size() < expected_len) {
            return {std::nullopt, ParseError::PayloadMismatch};
        }

        size_t authenticated_len = sizeof(FrameHeader) + header.payload_len;
        auto authenticated_data = frame_bytes.subspan(0, authenticated_len);
        auto received_tag = frame_bytes.subspan(authenticated_len, TagSize);

        Tag computed_tag = compute_hmac(key_, authenticated_data);
        if (!constant_time_equal(received_tag, std::span{computed_tag})) {
            return {std::nullopt, ParseError::AuthFailed};
        }

        if (current_time > 0 && max_time_drift > 0) {
            uint32_t diff = (current_time >= header.timestamp)
                          ? (current_time - header.timestamp)
                          : (header.timestamp - current_time);
            if (diff > max_time_drift) {
                return {std::nullopt, ParseError::TimestampExpired};
            }
        }

        if (!window_.check(header.seq_num)) {
            return {std::nullopt, ParseError::ReplayDetected};
        }

        window_.commit(header.seq_num);

        return {
            ValidatedCommand{
                header.msg_type,
                header.seq_num,
                header.timestamp,
                frame_bytes.subspan(sizeof(FrameHeader), header.payload_len)
            },
            std::nullopt
        };
    }

private:
    Key key_;
    ReplayWindow window_;

    static Tag compute_hmac(Key k, std::span<const uint8_t> data) noexcept {
        Tag tag{};
        uint32_t acc = 0x811C9DC5U;
        for (auto b : k) acc = (acc ^ b) * 0x01000193U;
        for (auto b : data) acc = (acc ^ b) * 0x01000193U;
        std::memcpy(tag.data(), &acc, sizeof(acc));
        return tag;
    }

    static bool constant_time_equal(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
        if (a.size() != b.size()) return false;
        uint8_t diff = 0;
        for (size_t i = 0; i < a.size(); ++i) {
            diff |= (a[i] ^ b[i]);
        }
        return diff == 0;
    }
};

} // namespace embedded::security
