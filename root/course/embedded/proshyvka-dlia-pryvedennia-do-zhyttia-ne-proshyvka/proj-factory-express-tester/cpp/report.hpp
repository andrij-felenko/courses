#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

#include "fct.hpp"

// Звіт складається в один статичний буфер і йде оператору конвеєра через
// службовий порт одним рядком JSON. Ні купи, ні потоків форматування.

namespace fct {

class JsonReport {
public:
    void begin() noexcept;
    void add(std::string_view name, const Outcome& outcome,
             std::uint32_t duration_us) noexcept;
    void finish(bool overall_pass, std::uint32_t total_us) noexcept;

private:
    static constexpr std::size_t kCapacity = 1024;
    // Хвіст звіту мусить влізти завжди: обрізаний посередині JSON оператор
    // не розбере взагалі, тому місце під нього тримаємо від початку.
    static constexpr std::size_t kTailReserve = 96;

    void put(std::string_view text) noexcept;      // з оглядом на резерв
    void put_tail(std::string_view text) noexcept; // у сам резерв, без перевірки
    void put_escaped(std::string_view text) noexcept;
    void put_int(std::int32_t value, bool tail = false) noexcept;
    void put_measured(const std::optional<Measured>& measured) noexcept;

    std::array<char, kCapacity> buf_{};
    std::size_t len_{0};
    bool truncated_{false};
    bool first_{true};
};

}  // namespace fct
