#include <cstdint>
#include <string>
#include <format>
#include <optional>
#include <span>

struct FormattedEvent {
    uint32_t    id{0};
    uint32_t    timeBootMs{0};
    uint16_t    sequence{0};
    uint8_t     internalLogLevel{0};
    uint8_t     externalSeverity{0};
    std::string displayText;
    std::string actionText;
};

// Декодування події за допомогою std::span та std::format (C++20)
std::optional<FormattedEvent> decodeAndFormatEvent(std::span<const uint8_t> payload) {
    constexpr size_t MinHeaderAndArgs = 13 + sizeof(uint8_t) + sizeof(float);
    if (payload.size() < MinHeaderAndArgs) {
        return std::nullopt;
    }

    const uint32_t id = unpackArgLE<uint32_t>(payload, 0);
    if (id != 0x8A12B4C0) {
        return std::nullopt;
    }

    FormattedEvent event{};
    event.id = id;
    event.timeBootMs = unpackArgLE<uint32_t>(payload, 4);
    event.sequence   = unpackArgLE<uint16_t>(payload, 8);

    const uint8_t logLevels = payload[12];
    event.internalLogLevel = (logLevels >> 4) & 0x0F;
    event.externalSeverity = logLevels & 0x0F;

    auto args = payload.subspan(13);
    const uint8_t sensorId  = unpackU8(args, 0);
    const float   deviation = unpackF32LE(args, 1);

    event.displayText = std::format(
        "Збій калібрування компаса №{} (відхилення: {:.1f}°)",
        sensorId, deviation
    );

    event.actionText = "Відійдіть на 15 метрів від металевих конструкцій та повторіть процедуру.";

    return event;
}
