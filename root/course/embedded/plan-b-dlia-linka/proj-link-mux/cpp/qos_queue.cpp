#include "qos_queue.hpp"

#include <algorithm>

namespace linkmux {

Frame Frame::make(Priority prio, std::span<const std::uint8_t> data,
                  std::uint16_t seq, std::uint32_t stampMs) noexcept {
    Frame frame;
    frame.seq     = seq;
    frame.len     = static_cast<std::uint16_t>(std::min(data.size(), kMaxPayload));
    frame.stampMs = stampMs;
    frame.prio    = prio;
    std::copy_n(data.begin(), frame.len, frame.payload.begin());
    return frame;
}

// Смуги мають різні типи (різна місткість), тому розгалуження явне —
// воно читається краще за будь-який шаблонний диспетчер на три випадки.
bool TxQueues::push(Priority prio, const Frame& frame) noexcept {
    switch (prio) {
    case Priority::Critical:  return critical_.push(frame);
    case Priority::Telemetry: return telemetry_.push(frame);
    case Priority::Video:     return video_.push(frame);
    }
    return false;
}

const Frame* TxQueues::front(Priority prio) const noexcept {
    switch (prio) {
    case Priority::Critical:  return critical_.front();
    case Priority::Telemetry: return telemetry_.front();
    case Priority::Video:     return video_.front();
    }
    return nullptr;
}

void TxQueues::popFront(Priority prio) noexcept {
    switch (prio) {
    case Priority::Critical:  critical_.popFront(); break;
    case Priority::Telemetry: telemetry_.popFront(); break;
    case Priority::Video:     video_.popFront(); break;
    }
}

void TxQueues::flush(Priority prio) noexcept {
    switch (prio) {
    case Priority::Critical:  critical_.flush(); break;
    case Priority::Telemetry: telemetry_.flush(); break;
    case Priority::Video:     video_.flush(); break;
    }
}

std::size_t TxQueues::size(Priority prio) const noexcept {
    switch (prio) {
    case Priority::Critical:  return critical_.size();
    case Priority::Telemetry: return telemetry_.size();
    case Priority::Video:     return video_.size();
    }
    return 0;
}

std::uint32_t TxQueues::dropped(Priority prio) const noexcept {
    switch (prio) {
    case Priority::Critical:  return critical_.dropped();
    case Priority::Telemetry: return telemetry_.dropped();
    case Priority::Video:     return video_.dropped();
    }
    return 0;
}

}  // namespace linkmux
