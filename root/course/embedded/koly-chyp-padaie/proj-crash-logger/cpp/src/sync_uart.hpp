// Синхронний порт: єдиний вивід, дозволений в аварійному обробнику. Помилку
// передавача віддаємо через std::expected — мовчазний -1 тут нікому не потрібен,
// а виняток у обробнику винятку не має жодного сенсу.
#pragma once

#include <array>
#include <cstdint>
#include <expected>
#include <optional>
#include <string_view>

namespace io {

enum class TxError { Timeout };

using TxResult = std::expected<void, TxError>;

// Форматування без printf: значення повертається масивом за значенням, тож
// жодних спільних буферів і жодної залежності від порядку викликів.
[[nodiscard]] std::array<char, 10> to_hex(std::uint32_t value) noexcept;

namespace console {

void init(std::uint32_t pclk_hz, std::uint32_t baud) noexcept;

TxResult write(std::string_view text) noexcept;
TxResult write_hex(std::uint32_t value) noexcept;
TxResult write_dec(std::uint32_t value) noexcept;
TxResult newline() noexcept;

// Порожнє значення означає «в приймачі нічого немає», а не помилку.
[[nodiscard]] std::optional<char> read() noexcept;

} // namespace console
} // namespace io
