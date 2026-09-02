#pragma once

#include <chrono>
#include <expected>
#include <span>
#include <string_view>

#include "rc/channels.hpp"

// Кадри CRSF і SBUS плюс нагляд за лінком: обидва протоколи віддають той
// самий RawChannels, тож вище за цей шар різниці між ними немає.
namespace rc {

enum class ParseError : std::uint8_t {
    TooShort,
    BadAddress,
    BadLength,
    BadType,
    BadCrc,
    BadHeader,
    BadFooter,
};

[[nodiscard]] std::string_view describe(ParseError err) noexcept;

namespace crsf {

inline constexpr std::uint8_t  kAddrFlightController = 0xC8;
inline constexpr std::uint8_t  kFrameTypeRcChannelsPacked = 0x16;
inline constexpr std::uint8_t  kCrcPoly = 0xD5;
inline constexpr std::size_t   kRcFrameSize = 26;   // адреса + довжина + тип + 22 + CRC
inline constexpr std::uint8_t  kRcLengthField = 24; // тип + канали + CRC

using RcFrame = std::array<std::uint8_t, kRcFrameSize>;

[[nodiscard]] std::uint8_t crc8(std::span<const std::uint8_t> data) noexcept;
[[nodiscard]] std::expected<RawChannels, ParseError> parseRcChannels(
    std::span<const std::uint8_t> frame) noexcept;
[[nodiscard]] RcFrame buildRcChannels(const RawChannels& raw) noexcept;

}  // namespace crsf

namespace sbus {

inline constexpr std::size_t  kFrameSize = 25;
inline constexpr std::uint8_t kHeader    = 0x0F;
inline constexpr std::uint8_t kFooter    = 0x00;
inline constexpr std::uint8_t kFooterV2  = 0x04;  // Futaba S.BUS2

inline constexpr std::uint8_t kFlagCh17      = 0x01;
inline constexpr std::uint8_t kFlagCh18      = 0x02;
inline constexpr std::uint8_t kFlagFrameLost = 0x04;
inline constexpr std::uint8_t kFlagFailsafe  = 0x08;

using Frame = std::array<std::uint8_t, kFrameSize>;

struct Packet {
    RawChannels channels{};
    bool ch17{false};
    bool ch18{false};
    bool frameLost{false};
    bool failsafe{false};
};

[[nodiscard]] std::expected<Packet, ParseError> parse(std::span<const std::uint8_t> frame) noexcept;
[[nodiscard]] Frame build(const Packet& packet) noexcept;

}  // namespace sbus

// Поведінка приймача при втраті радіосигналу
enum class FailsafePolicy : std::uint8_t {
    Cut,            // приймач мовчить, контролер ловить таймаут
    HoldLastState,  // приймач повторює останні значення — заборонено
    PresetValues,   // приймач сам виставляє наперед задані значення
};

inline constexpr auto kFailsafeTimeout = std::chrono::milliseconds{100};
inline constexpr std::uint16_t kFailsafeThrottleUs = 950;  // нижче порога виявлення

class LinkMonitor {
public:
    LinkMonitor(ChannelMap map, FailsafePolicy policy, std::size_t modeChannel) noexcept;

    void onFrame(const RawChannels& raw, std::chrono::milliseconds now, bool rxFailsafeBit) noexcept;
    bool tick(std::chrono::milliseconds now) noexcept;  // true — failsafe діє

    [[nodiscard]] const MicrosChannels& channelsUs() const noexcept { return us_; }
    [[nodiscard]] bool failsafe() const noexcept { return failsafe_; }

private:
    void applyPolicy() noexcept;

    ChannelMap     map_;
    FailsafePolicy policy_;
    std::size_t    modeChannel_;
    std::chrono::milliseconds lastFrame_{};
    bool           failsafe_{false};
    MicrosChannels us_{};
};

}  // namespace rc
