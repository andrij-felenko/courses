#include <cstdint>
#include <cstddef>
#include <span>
#include <functional>
#include <vector>

class SlipDecoder {
public:
    enum class State : uint8_t {
        Normal = 0,
        Escaped
    };

    static constexpr uint8_t EndVal    = 0xC0;
    static constexpr uint8_t EscVal    = 0xDB;
    static constexpr uint8_t EscEndVal = 0xDC;
    static constexpr uint8_t EscEscVal = 0xDD;

    using PacketCallback = std::function<void(std::span<const uint8_t>)>;

    SlipDecoder(std::span<uint8_t> storage, PacketCallback callback) noexcept
        : buffer_(storage), callback_(std::move(callback)) {}

    void reset() noexcept {
        write_pos_ = 0;
        state_ = State::Normal;
        overflow_ = false;
    }

    void feed(uint8_t byte) noexcept {
        switch (state_) {
        case State::Normal:
            if (byte == EndVal) {
                if (write_pos_ > 0) {
                    if (!overflow_ && callback_) {
                        callback_(std::span<const uint8_t>(buffer_.data(), write_pos_));
                    }
                    write_pos_ = 0;
                    overflow_ = false;
                }
            } else if (byte == EscVal) {
                state_ = State::Escaped;
            } else {
                append_byte(byte);
            }
            break;

        case State::Escaped:
            if (byte == EscEndVal) {
                append_byte(EndVal);
                state_ = State::Normal;
            } else if (byte == EscEscVal) {
                append_byte(EscVal);
                state_ = State::Normal;
            } else if (byte == EndVal) {
                /* Порушення послідовності: скидаємо пакет */
                write_pos_ = 0;
                overflow_ = false;
                state_ = State::Normal;
            } else {
                append_byte(byte);
                state_ = State::Normal;
            }
            break;
        }
    }

    void feed(std::span<const uint8_t> chunk) noexcept {
        for (uint8_t b : chunk) {
            feed(b);
        }
    }

    [[nodiscard]] size_t current_size() const noexcept { return write_pos_; }
    [[nodiscard]] bool has_overflow() const noexcept { return overflow_; }

private:
    void append_byte(uint8_t b) noexcept {
        if (write_pos_ < buffer_.size()) {
            buffer_[write_pos_++] = b;
        } else {
            overflow_ = true;
        }
    }

    std::span<uint8_t> buffer_;
    PacketCallback callback_;
    size_t write_pos_{0};
    State state_{State::Normal};
    bool overflow_{false};
};

class SlipEncoder {
public:
    static constexpr uint8_t EndVal    = 0xC0;
    static constexpr uint8_t EscVal    = 0xDB;
    static constexpr uint8_t EscEndVal = 0xDC;
    static constexpr uint8_t EscEscVal = 0xDD;

    /* Кодування в заздалегідь виділений буфер */
    static size_t encode(std::span<const uint8_t> src, std::span<uint8_t> dst) noexcept {
        size_t out_pos = 0;
        if (dst.empty()) return 0;

        dst[out_pos++] = EndVal;

        for (uint8_t b : src) {
            if (b == EndVal) {
                if (out_pos + 2 > dst.size()) return 0;
                dst[out_pos++] = EscVal;
                dst[out_pos++] = EscEndVal;
            } else if (b == EscVal) {
                if (out_pos + 2 > dst.size()) return 0;
                dst[out_pos++] = EscVal;
                dst[out_pos++] = EscEscVal;
            } else {
                if (out_pos + 1 > dst.size()) return 0;
                dst[out_pos++] = b;
            }
        }

        if (out_pos >= dst.size()) return 0;
        dst[out_pos++] = EndVal;
        return out_pos;
    }

    /* Зручне кодування у вектор для високорівневого коду */
    static std::vector<uint8_t> encode_to_vector(std::span<const uint8_t> src) {
        std::vector<uint8_t> out;
        out.reserve(src.size() + 8);
        out.push_back(EndVal);

        for (uint8_t b : src) {
            if (b == EndVal) {
                out.push_back(EscVal);
                out.push_back(EscEndVal);
            } else if (b == EscVal) {
                out.push_back(EscVal);
                out.push_back(EscEscVal);
            } else {
                out.push_back(b);
            }
        }

        out.push_back(EndVal);
        return out;
    }
};
