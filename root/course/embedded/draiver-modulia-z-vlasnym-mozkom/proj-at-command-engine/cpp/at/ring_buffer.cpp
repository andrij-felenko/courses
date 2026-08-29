#include "at/ring_buffer.hpp"

namespace at {

RingBuffer::Scan RingBuffer::find(std::uint16_t head, std::uint8_t needle,
                                  std::size_t limit) const noexcept
{
    std::uint16_t scan = tail_;
    std::size_t walked = 0;

    while (scan != head) {
        if (data_[scan] == needle) {
            return {Scan::Outcome::Found, scan};
        }
        scan = static_cast<std::uint16_t>((scan + 1) & config::kRxMask);
        ++walked;

        if (walked >= limit) {
            /* Потік без термінаторів: завади в ефірі, неузгоджена швидкість,
               двійкове сміття після скидання модуля. Без цієї стелі парсер
               став би назавжди, а буфер заповнився б до кінця. */
            return {Scan::Outcome::LimitExceeded, scan};
        }
    }
    return {Scan::Outcome::Incomplete, scan};
}

std::size_t RingBuffer::drain_to(std::uint16_t stop, std::span<char> out) noexcept
{
    std::size_t written = 0;

    while (tail_ != stop) {
        const auto byte = data_[tail_];
        if (byte != static_cast<std::uint8_t>('\r') && written < out.size()) {
            out[written++] = static_cast<char>(byte);
        }
        tail_ = static_cast<std::uint16_t>((tail_ + 1) & config::kRxMask);
    }
    tail_ = static_cast<std::uint16_t>((tail_ + 1) & config::kRxMask);  // з'їдаємо термінатор
    return written;
}

bool RingBuffer::take_upto(std::uint16_t head, std::uint8_t needle) noexcept
{
    const Scan scan = find(head, needle, config::kRxSize);
    if (scan.outcome != Scan::Outcome::Found) {
        return false;
    }
    tail_ = static_cast<std::uint16_t>((scan.index + 1) & config::kRxMask);
    return true;
}

}  // namespace at
