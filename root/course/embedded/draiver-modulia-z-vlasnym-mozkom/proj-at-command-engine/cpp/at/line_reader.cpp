#include "at/line_reader.hpp"

#include <algorithm>

namespace at {

std::expected<std::string_view, LineReader::Event> LineReader::next(std::uint16_t head) noexcept
{
    if (ring_.available(head) == 0) {
        return std::unexpected{Event::NoData};
    }

    const RingBuffer::Scan scan =
        ring_.find(head, static_cast<std::uint8_t>('\n'), config::kMaxLine);

    switch (scan.outcome) {
        case RingBuffer::Scan::Outcome::Incomplete:
            /* Модуль розірвав відповідь між кадрами. Нічого не споживаємо —
               решта прийде наступним викликом. */
            return std::unexpected{Event::NoData};

        case RingBuffer::Scan::Outcome::LimitExceeded:
            ring_.seek(scan.index);
            return std::unexpected{Event::Overflow};

        case RingBuffer::Scan::Outcome::Found:
            break;
    }

    const std::size_t written = ring_.drain_to(scan.index, scratch_);
    const std::string_view line{scratch_.data(), written};

    /* Порожній рядок і рядок із самих пробілів (хвіст запрошення "> ")
       рівноцінні: змісту немає, розбирати нічого. */
    const bool visible = std::ranges::any_of(line, [](char c) { return c > ' '; });
    if (!visible) {
        return std::unexpected{Event::Blank};
    }
    return line;
}

}  // namespace at
