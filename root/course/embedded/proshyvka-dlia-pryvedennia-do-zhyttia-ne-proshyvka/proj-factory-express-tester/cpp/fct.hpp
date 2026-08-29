#pragma once

#include <cstdint>
#include <expected>
#include <optional>
#include <string_view>

#include "hal.hpp"

// Ядро тестового рушія. Результат тесту — std::expected: успіх несе
// виміряне число, провал — код і причину. Рядки завжди статичні літерали,
// тому string_view тут безпечний і копіювати нічого не треба.

namespace fct {

enum class Error : std::uint8_t {
    Fail,
    Timeout,
    BusLocked,
    InvalidId,
    Skipped
};

struct Measured {
    std::int32_t value{};
    std::string_view unit{};
};

struct Success {
    std::string_view note{};
    std::optional<Measured> measured{};
};

struct Failure {
    Error code{Error::Fail};
    std::string_view detail{};
    std::optional<Measured> measured{};
};

using Outcome = std::expected<Success, Failure>;

// Зручні конструктори провалу — щоб у тестах не було std::unexpected{...}
// на пів рядка.
[[nodiscard]] inline std::unexpected<Failure> fail(Error code,
                                                   std::string_view detail) noexcept
{
    return std::unexpected(Failure{code, detail, std::nullopt});
}

[[nodiscard]] inline std::unexpected<Failure> fail(Error code, std::string_view detail,
                                                   std::int32_t value,
                                                   std::string_view unit) noexcept
{
    return std::unexpected(Failure{code, detail, Measured{value, unit}});
}

[[nodiscard]] inline Success pass(std::string_view note, std::int32_t value,
                                  std::string_view unit) noexcept
{
    return Success{note, Measured{value, unit}};
}

constexpr std::string_view to_string(Error code) noexcept
{
    switch (code) {
    case Error::Fail:      return "FAIL";
    case Error::Timeout:   return "TIMEOUT";
    case Error::BusLocked: return "BUS_LOCKED";
    case Error::InvalidId: return "INVALID_ID";
    case Error::Skipped:   return "SKIPPED";
    }
    return "UNKNOWN";
}

// Єдиний дозволений спосіб чекати на апаратуру: очікування завжди має дно.
class Deadline {
public:
    explicit Deadline(std::uint32_t limit_us) noexcept
        : start_{hal::time_us()}, limit_{limit_us} {}

    [[nodiscard]] std::uint32_t elapsed_us() const noexcept
    {
        return hal::time_us() - start_;  // беззнакова різниця переживає обгортку
    }

    [[nodiscard]] bool expired() const noexcept { return elapsed_us() >= limit_; }

private:
    std::uint32_t start_;
    std::uint32_t limit_;
};

// PRIMASK як RAII: жодного шляху виходу без відновлення переривань.
class IrqMask {
public:
    IrqMask() noexcept : saved_{hal::irq_disable()} {}
    ~IrqMask() { hal::irq_restore(saved_); }

    IrqMask(const IrqMask&) = delete;
    IrqMask& operator=(const IrqMask&) = delete;

private:
    std::uint32_t saved_;
};

using TestFn = Outcome (*)() noexcept;

struct Case {
    std::string_view name;
    TestFn run;
    std::uint32_t budget_us;
    bool blocking;   // провал зупиняє весь набір
};

}  // namespace fct
