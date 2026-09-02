#pragma once

#include <expected>
#include <string_view>
#include <variant>

#include "option_config.hpp"

namespace optbytes {

// Відмови заліза — на відміну від Policy, ці трапляються вже під час запису.
enum class Hardware : std::uint8_t {
    SupplyTooLow,     // VDD просіла: зарядова помпа не дотисне комірку
    BusyTimeout,      // контролер не звільнив BSY
    UnlockRejected,   // ключі не зняли блокування
    ProgrammingError, // апаратний прапорець помилки в SR
    VerifyMismatch,   // прочитане не збіглося з бажаним
    ReloadStalled,    // записали, але OBL_LAUNCH не скинув чип
};

std::string_view describe(Hardware error) noexcept;

// Дві природи відмови не змішуємо в один enum: політика зупиняє нас ДО того,
// як щось пішло в залізо, і читається на місці помилки саме так.
using Error = std::variant<Policy, Hardware>;

std::string_view describe(const Error& error) noexcept;

class OptionBytes {
public:
    [[nodiscard]] static Config read() noexcept;

    // Повний протокол: політика → живлення → ключі → OPTSTRT → звірка →
    // OBL_LAUNCH. За успіху не повертається: перезавантаження опцій скидає чип.
    [[nodiscard]] static std::expected<void, Error> apply(const Config& wanted) noexcept;

private:
    class Session; // RAII довкола пари блокувань контролера Flash
};

} // namespace optbytes
