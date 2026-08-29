#include "framing.hpp"

#include <algorithm>

#include "codec.hpp"

namespace link {

std::expected<Bytes, Error> build_frame(std::uint8_t seq, Bytes payload,
                                        std::span<std::uint8_t> wire) noexcept {
    if (payload.size() > kMaxPayload) {
        return std::unexpected(Error::TooLong);
    }
    if (wire.size() < 2) {
        return std::unexpected(Error::NoSpace);
    }

    std::array<std::uint8_t, kMaxFrame> frame{};
    frame[0] = seq;
    std::ranges::copy(payload, frame.begin() + kSeqSize);

    const std::size_t body = kSeqSize + payload.size();
    const std::uint16_t crc = codec::crc16_ccitt(Bytes{frame.data(), body});
    frame[body]     = static_cast<std::uint8_t>(crc >> 8);
    frame[body + 1] = static_cast<std::uint8_t>(crc & 0xFF);

    // Один байт місткості лишаємо під роздільник.
    const auto encoded = codec::cobs_encode(Bytes{frame.data(), body + kCrcSize},
                                            wire.first(wire.size() - 1));
    if (!encoded) {
        return std::unexpected(encoded.error());
    }

    wire[*encoded] = kDelimiter;
    return Bytes{wire.data(), *encoded + 1};
}

void FrameReader::feed(Bytes chunk) {
    for (const std::uint8_t byte : chunk) {
        feed_byte(byte);
    }
}

void FrameReader::feed_byte(std::uint8_t byte) {
    if (byte != kDelimiter) {
        if (raw_len_ >= raw_.size()) {
            // Кадр не закінчився там, де мав: усе до наступного 0x00 — сміття.
            if (!desync_) {
                desync_ = true;
                ++stats_.overflows;
            }
            return;
        }
        raw_[raw_len_++] = byte;
        return;
    }

    // Роздільник — точка, у якій приймач завжди повертається в синхронізм.
    if (desync_) {
        raw_len_ = 0;
        desync_ = false;
        return;
    }
    if (raw_len_ == 0) {
        return;   // тиша в лінії або два роздільники поспіль
    }

    finish_frame();
}

void FrameReader::finish_frame() {
    const auto decoded = codec::cobs_decode(Bytes{raw_.data(), raw_len_}, frame_);
    raw_len_ = 0;

    if (!decoded) {
        ++stats_.cobs_errors;
        return;
    }

    const std::size_t len = *decoded;
    if (len < kSeqSize + kCrcSize) {
        ++stats_.crc_errors;
        return;
    }
    // Остача над блоком РАЗОМ із CRC мусить дорівнювати нулю.
    if (codec::crc16_ccitt(Bytes{frame_.data(), len}) != 0) {
        ++stats_.crc_errors;
        return;
    }

    ++stats_.frames;
    if (on_frame_) {
        on_frame_(Frame{frame_[0], Bytes{frame_.data() + kSeqSize, len - kSeqSize - kCrcSize}});
    }
}

}  // namespace link
