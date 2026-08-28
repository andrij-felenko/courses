#include <cstdint>
#include <cstddef>
#include <span>
#include <functional>
#include <vector>

class SlipStreamParser {
public:
    enum class State : uint8_t { Normal, Escaped };

    static constexpr uint8_t DelimiterEnd    = 0xC0;
    static constexpr uint8_t PrefixEsc       = 0xDB;
    static constexpr uint8_t SubstringEscEnd = 0xDC;
    static constexpr uint8_t SubstringEscEsc = 0xDD;

    using FrameHandler = std::function<void(std::span<const uint8_t>)>;

    SlipStreamParser(std::span<uint8_t> buffer, FrameHandler handler) noexcept
        : rx_buffer_(buffer), handler_(std::move(handler)) {}

    void parse_byte(uint8_t byte) noexcept {
        if (state_ == State::Normal) {
            if (byte == DelimiterEnd) {
                if (write_index_ > 0) {
                    if (!overflow_flag_ && handler_) {
                        handler_(std::span<const uint8_t>(rx_buffer_.data(), write_index_));
                    }
                    write_index_ = 0;
                    overflow_flag_ = false;
                }
            } else if (byte == PrefixEsc) {
                state_ = State::Escaped;
            } else {
                store_byte(byte);
            }
        } else { /* State::Escaped */
            if (byte == SubstringEscEnd) {
                store_byte(DelimiterEnd);
            } else if (byte == SubstringEscEsc) {
                store_byte(PrefixEsc);
            } else {
                store_byte(byte);
            }
            state_ = State::Normal;
        }
    }

    void parse_chunk(std::span<const uint8_t> bytes) noexcept {
        for (uint8_t b : bytes) {
            parse_byte(b);
        }
    }

    void reset() noexcept {
        write_index_ = 0;
        state_ = State::Normal;
        overflow_flag_ = false;
    }

private:
    void store_byte(uint8_t b) noexcept {
        if (write_index_ < rx_buffer_.size()) {
            rx_buffer_[write_index_++] = b;
        } else {
            overflow_flag_ = true;
        }
    }

    std::span<uint8_t> rx_buffer_;
    FrameHandler handler_;
    size_t write_index_{0};
    State state_{State::Normal};
    bool overflow_flag_{false};
};

class SlipStreamPacker {
public:
    static size_t pack(std::span<const uint8_t> src, std::span<uint8_t> dst) noexcept {
        size_t out_idx = 0;
        if (dst.empty()) return 0;

        dst[out_idx++] = SlipStreamParser::DelimiterEnd;

        for (uint8_t b : src) {
            if (b == SlipStreamParser::DelimiterEnd) {
                if (out_idx + 2 > dst.size()) return 0;
                dst[out_idx++] = SlipStreamParser::PrefixEsc;
                dst[out_idx++] = SlipStreamParser::SubstringEscEnd;
            } else if (b == SlipStreamParser::PrefixEsc) {
                if (out_idx + 2 > dst.size()) return 0;
                dst[out_idx++] = SlipStreamParser::PrefixEsc;
                dst[out_idx++] = SlipStreamParser::SubstringEscEsc;
            } else {
                if (out_idx + 1 > dst.size()) return 0;
                dst[out_idx++] = b;
            }
        }

        if (out_idx >= dst.size()) return 0;
        dst[out_idx++] = SlipStreamParser::DelimiterEnd;
        return out_idx;
    }
};
