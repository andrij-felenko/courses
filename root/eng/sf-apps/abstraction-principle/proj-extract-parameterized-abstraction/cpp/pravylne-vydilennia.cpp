#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>

// ── 1. Контракт через C++20 Concept (перевірка під час компіляції) ──
template <typename P>
concept FramePolicy = requires(uint8_t crc, uint8_t byte) {
    { P::header } -> std::convertible_to<std::span<const uint8_t>>;
    { P::max_payload } -> std::convertible_to<size_t>;
    { P::initial_crc } -> std::convertible_to<uint8_t>;
    { P::update_crc(crc, byte) } -> std::same_as<uint8_t>;
};

// ── 2. Параметризований FSM з нульовими накладними витратами ────────
template <FramePolicy Policy>
class StreamFramer {
public:
    template <typename Callback>
    bool feed_byte(uint8_t byte, Callback&& on_frame) {
        switch (state_) {
            case State::Header:
                if (byte == Policy::header[header_matched_]) {
                    if (++header_matched_ == Policy::header.size()) {
                        state_ = State::Length;
                        header_matched_ = 0;
                        payload_len_ = 0;
                        crc_ = Policy::initial_crc;
                    }
                } else {
                    header_matched_ = (byte == Policy::header[0]) ? 1 : 0;
                }
                break;

            case State::Length:
                expected_len_ = byte;
                crc_ = Policy::update_crc(crc_, byte);
                if (byte <= buffer_.size() && byte <= Policy::max_payload) {
                    state_ = State::Payload;
                } else {
                    state_ = State::Header;
                }
                break;

            case State::Payload:
                buffer_[payload_len_++] = byte;
                crc_ = Policy::update_crc(crc_, byte);
                if (payload_len_ == expected_len_) {
                    state_ = State::Crc;
                }
                break;

            case State::Crc:
                state_ = State::Header;
                if (crc_ == byte) {
                    on_frame(std::span<const uint8_t>(buffer_.data(), payload_len_));
                    return true;
                }
                break;
        }
        return false;
    }

private:
    enum class State : uint8_t { Header, Length, Payload, Crc };

    std::array<uint8_t, Policy::max_payload> buffer_{};
    size_t payload_len_{0};
    size_t expected_len_{0};
    size_t header_matched_{0};
    uint8_t crc_{Policy::initial_crc};
    State state_{State::Header};
};

// ── 3. Статичні описи протоколів (дані застигають під час збірки) ────

struct GnssPolicy {
    static constexpr uint8_t hdr_bytes[] = { 0xAA, 0x55 };
    static constexpr std::span<const uint8_t> header{hdr_bytes};
    static constexpr size_t max_payload = 128;
    static constexpr uint8_t initial_crc = 0x00;

    static constexpr uint8_t update_crc(uint8_t crc, uint8_t byte) noexcept {
        return crc ^ byte;
    }
};

struct OpticPolicy {
    static constexpr uint8_t hdr_bytes[] = { 0x24 };
    static constexpr std::span<const uint8_t> header{hdr_bytes};
    static constexpr size_t max_payload = 64;
    static constexpr uint8_t initial_crc = 0xFF;

    static constexpr uint8_t update_crc(uint8_t crc, uint8_t byte) noexcept {
        return static_cast<uint8_t>(crc + byte);
    }
};

// Конкретні типи парсерів створюються інстанціюванням єдиного шаблону:
using GnssFramer = StreamFramer<GnssPolicy>;
using OpticFramer = StreamFramer<OpticPolicy>;
