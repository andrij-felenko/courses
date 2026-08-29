#pragma once

#include <charconv>
#include <cstdint>
#include <expected>
#include <string>
#include <string_view>

#include "node_state.hpp"

/*
 * Розбір і складання документів тіні пристрою.
 * Дельта — плаский об'єкт без вкладень і масивів, саме так її шле брокер:
 *   {"version":9,"temp":24.5,"fan":2400,"heat":true}
 * Тут судимо ЛИШЕ синтаксис і типи; фізичні межі судить агент стану.
 */
namespace iot {

enum class ParseError : std::uint8_t {
    Malformed,  /* значення не розібралося як число чи логічне */
    NoVersion   /* документ без версії застосовувати не можна */
};

[[nodiscard]] std::string_view describe(ParseError error) noexcept;

[[nodiscard]] std::expected<ConfigDelta, ParseError> parseDelta(std::string_view doc) noexcept;

[[nodiscard]] std::string buildReported(const NodeConfig& config);

/* Людський опис набору полів — для журналу. */
[[nodiscard]] std::string describeFields(const ConfigDelta& delta);

} // namespace iot
