#include "report.hpp"

#include <algorithm>

#include "hal.hpp"

namespace fct {

void JsonReport::put(std::string_view text) noexcept
{
    if (len_ + text.size() > kCapacity - kTailReserve) {
        truncated_ = true;
        return;
    }
    std::copy(text.begin(), text.end(), buf_.begin() + len_);
    len_ += text.size();
}

void JsonReport::put_tail(std::string_view text) noexcept
{
    const std::size_t room = std::min(text.size(), kCapacity - len_);
    std::copy_n(text.begin(), room, buf_.begin() + len_);
    len_ += room;
}

// Рядки в звіті — наші власні літерали, але екрануємо все одно: одна лапка
// в описі помилки зламала б парсер на стороні стенда.
void JsonReport::put_escaped(std::string_view text) noexcept
{
    for (const char c : text) {
        if (c == '"' || c == '\\') {
            const char pair[2]{'\\', c};
            put(std::string_view{pair, 2});
        } else if (static_cast<unsigned char>(c) >= 0x20) {
            put(std::string_view{&c, 1});
        } else {
            put(" ");
        }
    }
}

void JsonReport::put_int(std::int32_t value, bool tail) noexcept
{
    std::array<char, 12> digits{};
    std::size_t n = 0;
    auto magnitude = value < 0 ? static_cast<std::uint32_t>(-static_cast<std::int64_t>(value))
                               : static_cast<std::uint32_t>(value);

    if (value < 0) {
        tail ? put_tail("-") : put("-");
    }
    do {
        digits[n++] = static_cast<char>('0' + magnitude % 10);
        magnitude /= 10;
    } while (magnitude != 0);

    while (n > 0) {
        --n;
        const std::string_view one{&digits[n], 1};
        tail ? put_tail(one) : put(one);
    }
}

void JsonReport::put_measured(const std::optional<Measured>& measured) noexcept
{
    if (!measured) {
        return;
    }
    put(",\"value\":");
    put_int(measured->value);
    put(",\"unit\":\"");
    put_escaped(measured->unit);
    put("\"");
}

void JsonReport::begin() noexcept
{
    len_ = 0;
    truncated_ = false;
    first_ = true;
    put("{\"fct\":[");
}

void JsonReport::add(std::string_view name, const Outcome& outcome,
                     std::uint32_t duration_us) noexcept
{
    if (!first_) {
        put(",");
    }
    first_ = false;

    put("{\"test\":\"");
    put_escaped(name);
    put("\",\"status\":\"");
    put(outcome ? std::string_view{"PASS"} : to_string(outcome.error().code));
    put("\",\"us\":");
    put_int(static_cast<std::int32_t>(duration_us));

    if (outcome) {
        if (!outcome->note.empty()) {
            put(",\"detail\":\"");
            put_escaped(outcome->note);
            put("\"");
        }
        put_measured(outcome->measured);
    } else {
        put(",\"detail\":\"");
        put_escaped(outcome.error().detail);
        put("\"");
        put_measured(outcome.error().measured);
    }
    put("}");
}

void JsonReport::finish(bool overall_pass, std::uint32_t total_us) noexcept
{
    put_tail("],\"verdict\":\"");
    put_tail(overall_pass ? "PASS" : "FAIL");
    put_tail("\",\"total_us\":");
    put_int(static_cast<std::int32_t>(total_us), true);
    if (truncated_) {
        put_tail(",\"truncated\":true");
    }
    put_tail("}\r\n");

    hal::uart_write(std::span<const char>{buf_.data(), len_});
}

}  // namespace fct
