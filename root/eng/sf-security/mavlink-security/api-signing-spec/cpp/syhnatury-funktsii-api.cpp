#include <cstdint>
#include <span>
#include <string_view>

class IMavlinkSigningEngine {
public:
    virtual ~IMavlinkSigningEngine() = default;

    // Підписання повідомлення та упаковка в буфер відправки
    virtual uint16_t signMessage(
        uint8_t channel,
        std::span<uint8_t> out_buffer,
        const MavlinkMessage& msg,
        MavlinkSigningContext& signing_ctx
    ) = 0;

    // Перевірка валідності вхідного підписаного кадру
    virtual bool verifyMessage(
        const MavlinkMessage& msg,
        const MavlinkStatus& status,
        MavlinkSigningContext& signing_ctx
    ) = 0;
};
