#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

#include "at/command.hpp"
#include "at/config.hpp"
#include "at/static_string.hpp"

namespace at {

/* Табличний диспетчер спонтанних сповіщень.

   Обробник викликається з контексту головного циклу (зсередини Engine::poll),
   а не з переривання UART. Це не деталь реалізації, а умова: класти команду
   в чергу зсередини ISR — це пошкоджені індекси або взаємне блокування. */
class UrcTable {
public:
    bool add(std::string_view prefix, UrcHandler handler) noexcept;

    /* Пошук за найдовшим збігом: "+QIURC: \"closed\"" мусить виграти в
       загального "+QIURC:", інакше окремий обробник розриву не спрацює. */
    bool dispatch(std::string_view line) noexcept;

    [[nodiscard]] std::size_t size() const noexcept { return count_; }

private:
    struct Entry {
        StaticString<config::kMaxPrefix> prefix{};
        UrcHandler handler{};
        std::uint32_t hits{0};
    };

    std::array<Entry, config::kMaxUrcHandlers> entry_{};
    std::size_t count_{0};
};

}  // namespace at
