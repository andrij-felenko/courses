#include "shadow_json.hpp"

#include <format>
#include <optional>

namespace iot {
namespace {

/* Знаходить "ключ": і повертає лексему значення до роздільника. */
std::optional<std::string_view> valueOf(std::string_view doc, std::string_view key) noexcept
{
    std::size_t from = 0;

    while (true) {
        const std::size_t at = doc.find(key, from);
        if (at == std::string_view::npos) {
            return std::nullopt;
        }
        from = at + key.size();

        /* Ключ мусить бути в лапках цілком, а не збігом за префіксом. */
        if (at == 0 || doc[at - 1] != '"' || from >= doc.size() || doc[from] != '"') {
            continue;
        }

        std::string_view rest = doc.substr(from + 1);
        const std::size_t colon = rest.find_first_not_of(" \t");
        if (colon == std::string_view::npos || rest[colon] != ':') {
            continue;
        }
        rest.remove_prefix(colon + 1);

        const std::size_t begin = rest.find_first_not_of(" \t");
        if (begin == std::string_view::npos) {
            return std::nullopt;
        }
        rest.remove_prefix(begin);

        const std::size_t end = rest.find_first_of(",}");
        std::string_view token = (end == std::string_view::npos) ? rest : rest.substr(0, end);

        const std::size_t last = token.find_last_not_of(" \t\r\n");
        return (last == std::string_view::npos) ? std::string_view{} : token.substr(0, last + 1);
    }
}

template <typename T>
std::optional<T> parseNumber(std::string_view token) noexcept
{
    T value{};
    const auto* first = token.data();
    const auto* last = token.data() + token.size();
    const auto result = std::from_chars(first, last, value);

    if (result.ec != std::errc{} || result.ptr != last) {
        return std::nullopt; /* у числі є сміття — документ покручений */
    }
    return value;
}

std::optional<bool> parseBool(std::string_view token) noexcept
{
    if (token == "true") {
        return true;
    }
    if (token == "false") {
        return false;
    }
    return std::nullopt;
}

} // namespace

std::string_view describe(ParseError error) noexcept
{
    switch (error) {
        case ParseError::Malformed:  return "покручений документ";
        case ParseError::NoVersion:  return "документ без версії";
    }
    return "невідомо";
}

std::expected<ConfigDelta, ParseError> parseDelta(std::string_view doc) noexcept
{
    ConfigDelta delta{};

    /* Версія обов'язкова: без неї немає захисту від застарілих пакетів,
       а отже й права застосовувати дельту до заліза. */
    const auto version = valueOf(doc, "version");
    if (!version) {
        return std::unexpected(ParseError::NoVersion);
    }
    const auto sequence = parseNumber<std::uint32_t>(*version);
    if (!sequence) {
        return std::unexpected(ParseError::NoVersion);
    }
    delta.sequenceId = *sequence;

    if (const auto token = valueOf(doc, "temp")) {
        const auto value = parseNumber<float>(*token);
        if (!value) {
            return std::unexpected(ParseError::Malformed);
        }
        delta.targetTemperature = *value;
    }
    if (const auto token = valueOf(doc, "fan")) {
        const auto value = parseNumber<std::uint16_t>(*token);
        if (!value) {
            return std::unexpected(ParseError::Malformed);
        }
        delta.fanSpeedRpm = *value;
    }
    if (const auto token = valueOf(doc, "heat")) {
        const auto value = parseBool(*token);
        if (!value) {
            return std::unexpected(ParseError::Malformed);
        }
        delta.heatingEnabled = *value;
    }

    return delta;
}

std::string buildReported(const NodeConfig& config)
{
    return std::format(
        R"({{"state":{{"reported":{{"temp":{:.1f},"fan":{},"heat":{}}}}},"version":{}}})",
        config.targetTemperature,
        config.fanSpeedRpm,
        config.heatingEnabled ? "true" : "false",
        config.sequenceId);
}

std::string describeFields(const ConfigDelta& delta)
{
    if (delta.empty()) {
        return "(немає)";
    }

    std::string out;
    if (delta.targetTemperature) {
        out += std::format(" уставка={:.1f}", *delta.targetTemperature);
    }
    if (delta.fanSpeedRpm) {
        out += std::format(" обертиВентилятора={}", *delta.fanSpeedRpm);
    }
    if (delta.heatingEnabled) {
        out += std::format(" нагрів={}", *delta.heatingEnabled ? "увімкнено" : "вимкнено");
    }
    return out;
}

} // namespace iot
