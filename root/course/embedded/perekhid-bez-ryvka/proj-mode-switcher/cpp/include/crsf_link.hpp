#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

namespace fc::crsf {

inline constexpr std::uint8_t kAddressFlightController = 0xC8;
inline constexpr std::uint8_t kTypeRcChannelsPacked = 0x16;
inline constexpr std::uint8_t kPayloadLen = 24;   // тип + 22 байти даних + crc
inline constexpr std::size_t kChannelCount = 16;
inline constexpr std::size_t kFrameSize = 26;

enum class Error { ShortFrame, BadAddress, BadLength, WrongType, BadCrc };

enum class SwitchPos { Low = 0, Mid = 1, High = 2 };

struct Channels {
    std::array<std::uint16_t, kChannelCount> raw{};

    [[nodiscard]] float microseconds(std::size_t index) const noexcept;
    [[nodiscard]] float unit(std::size_t index) const noexcept;   // 0..1
};

[[nodiscard]] std::uint8_t crc8(std::span<const std::uint8_t> data) noexcept;
[[nodiscard]] std::expected<Channels, Error> parse(std::span<const std::uint8_t> frame) noexcept;
[[nodiscard]] std::array<std::uint8_t, kFrameSize> pack(const Channels& channels) noexcept;

// Трипозиційний тумблер з гістерезисом: на межі позиція не має мерехтіти.
[[nodiscard]] SwitchPos switch_position(float microseconds, SwitchPos previous) noexcept;

class Link {
public:
    using Millis = std::chrono::milliseconds;
    static constexpr Millis kFailsafeTimeout{500};

    explicit Link(Millis now) noexcept : last_ok_{now} {}

    // Побитий кадр не оновлює ні канали, ні таймер: інакше шум на лінії
    // тримав би failsafe вимкненим при мертвому передавачі.
    std::expected<Channels, Error> feed(std::span<const std::uint8_t> frame, Millis now) noexcept;

    [[nodiscard]] bool tick(Millis now) noexcept;   // true = втрата зв'язку

    [[nodiscard]] const Channels& channels() const noexcept { return channels_; }
    [[nodiscard]] bool failsafe() const noexcept { return failsafe_; }
    [[nodiscard]] Millis silence(Millis now) const noexcept { return now - last_ok_; }
    [[nodiscard]] unsigned frames_ok() const noexcept { return frames_ok_; }
    [[nodiscard]] unsigned crc_errors() const noexcept { return crc_errors_; }
    [[nodiscard]] unsigned format_errors() const noexcept { return format_errors_; }

private:
    Channels channels_{};
    Millis last_ok_{};
    bool have_data_{false};
    bool failsafe_{true};   // доки жодного кадру не прийшло — довіри лінку нема
    unsigned frames_ok_{0};
    unsigned crc_errors_{0};
    unsigned format_errors_{0};
};

}  // namespace fc::crsf
