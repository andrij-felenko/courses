#pragma once

#include <array>
#include <cstdint>
#include <expected>
#include <string_view>

#include "at/config.hpp"
#include "at/ring_buffer.hpp"

namespace at {

/* Перетворює потік байтів на рядки. Окремий від RingBuffer навмисно: буфер
   знає про DMA й індекси, читач — про '\r\n' і стелю довжини рядка. */
class LineReader {
public:
    enum class Event : std::uint8_t {
        NoData,    // цілого рядка ще немає; tail лишився на місці
        Blank,     // порожній рядок або самі пробіли — розбирати нічого
        Overflow,  // перевищено kMaxLine, сміття викинуто
    };

    explicit LineReader(RingBuffer& ring) noexcept : ring_{ring} {}

    /* Повертає view у внутрішній буфер: дійсний до наступного виклику. */
    [[nodiscard]] std::expected<std::string_view, Event> next(std::uint16_t head) noexcept;

private:
    RingBuffer& ring_;
    std::array<char, config::kMaxLine> scratch_{};
};

}  // namespace at
