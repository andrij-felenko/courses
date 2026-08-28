#pragma once

#include <span>
#include <array>
#include <cstdint>
#include <cstddef>
#include <expected>
#include <concepts>
#include <algorithm>

namespace cobs {

enum class Status {
    Ok = 0,
    BufferOverflow,
    ZeroInPayload,
    UnexpectedDelimiter,
    InvalidOffset
};

[[nodiscard]] constexpr size_t max_encoded_length(size_t raw_len) noexcept {
    return raw_len + (raw_len / 254) + 1;
}

[[nodiscard]] constexpr std::expected<size_t, Status> encode(
    std::span<const uint8_t> src, 
    std::span<uint8_t> dst
) noexcept {
    if (dst.size() < max_encoded_length(src.size())) {
        return std::unexpected(Status::BufferOverflow);
    }

    size_t read_idx = 0;
    size_t write_idx = 1;
    size_t code_idx = 0;
    uint8_t code = 0x01;

    while (read_idx < src.size()) {
        const uint8_t byte = src[read_idx++];
        if (byte == 0x00) {
            dst[code_idx] = code;
            code_idx = write_idx++;
            code = 0x01;
        } else {
            dst[write_idx++] = byte;
            code++;
            if (code == 0xFF) {
                dst[code_idx] = code;
                code_idx = write_idx++;
                code = 0x01;
            }
        }
    }
    dst[code_idx] = code;
    return write_idx;
}

[[nodiscard]] constexpr std::expected<size_t, Status> decode(
    std::span<const uint8_t> src, 
    std::span<uint8_t> dst
) noexcept {
    if (src.empty()) return 0;

    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < src.size()) {
        const uint8_t code = src[read_idx++];
        if (code == 0x00) return std::unexpected(Status::ZeroInPayload);

        const size_t copy_len = code - 1;
        if (read_idx + copy_len > src.size()) {
            return std::unexpected(Status::InvalidOffset);
        }
        if (write_idx + copy_len > dst.size()) {
            return std::unexpected(Status::BufferOverflow);
        }

        for (size_t i = 0; i < copy_len; ++i) {
            dst[write_idx++] = src[read_idx++];
        }

        if (code < 0xFF && read_idx < src.size()) {
            if (write_idx >= dst.size()) {
                return std::unexpected(Status::BufferOverflow);
            }
            dst[write_idx++] = 0x00;
        }
    }

    return write_idx;
}

template <size_t MaxPacketSize>
class StreamingDecoder {
public:
    enum class State {
        HuntDelimiter,
        ReadCode,
        ReadData
    };

    constexpr StreamingDecoder() noexcept = default;

    template <typename Callback>
    requires std::invocable<Callback, std::span<const uint8_t>>
    Status feed(uint8_t byte, Callback&& on_packet_cb) noexcept {
        if (byte == 0x00) {
            if (state_ == State::ReadData && block_rem_ > 0) {
                rx_len_ = 0;
                state_ = State::ReadCode;
                return Status::UnexpectedDelimiter;
            }

            if (rx_len_ > 0) {
                std::span<const uint8_t> packet{buffer_.data(), rx_len_};
                rx_len_ = 0;
                state_ = State::ReadCode;
                std::forward<Callback>(on_packet_cb)(packet);
                return Status::Ok;
            }

            state_ = State::ReadCode;
            return Status::Ok;
        }

        switch (state_) {
        case State::HuntDelimiter:
            break;

        case State::ReadCode:
            code_ = byte;
            if (code_ == 0x01) {
                if (rx_len_ >= MaxPacketSize) {
                    reset_on_overflow();
                    return Status::BufferOverflow;
                }
                buffer_[rx_len_++] = 0x00;
            } else {
                block_rem_ = code_ - 1;
                state_ = State::ReadData;
            }
            break;

        case State::ReadData:
            if (rx_len_ >= MaxPacketSize) {
                reset_on_overflow();
                return Status::BufferOverflow;
            }

            buffer_[rx_len_++] = byte;
            block_rem_--;

            if (block_rem_ == 0) {
                if (code_ < 0xFF) {
                    if (rx_len_ >= MaxPacketSize) {
                        reset_on_overflow();
                        return Status::BufferOverflow;
                    }
                    buffer_[rx_len_++] = 0x00;
                }
                state_ = State::ReadCode;
            }
            break;
        }

        return Status::Ok;
    }

    [[nodiscard]] constexpr size_t current_length() const noexcept { return rx_len_; }
    constexpr void reset() noexcept {
        rx_len_ = 0;
        state_ = State::HuntDelimiter;
        code_ = 0;
        block_rem_ = 0;
    }

private:
    constexpr void reset_on_overflow() noexcept {
        rx_len_ = 0;
        state_ = State::HuntDelimiter;
    }

    std::array<uint8_t, MaxPacketSize> buffer_{};
    size_t rx_len_{0};
    State state_{State::HuntDelimiter};
    uint8_t code_{0};
    uint8_t block_rem_{0};
};

} // namespace cobs
