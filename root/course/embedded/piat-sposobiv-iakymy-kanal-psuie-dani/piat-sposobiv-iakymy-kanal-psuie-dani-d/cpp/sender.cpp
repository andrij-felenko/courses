#include "sender.hpp"

#include <algorithm>

namespace link {

Sender::Sender(ByteSink sink)
    : sink_(std::move(sink)),
      ack_reader_([this](const Frame& frame) { on_ack(frame); }) {}

void Sender::on_ack(const Frame& frame) {
    if (!frame.payload.empty()) {
        return;   // у зворотному напрямку ходять лише порожні кадри-квитанції
    }

    const auto it = std::ranges::find_if(slots_, [&](const Slot& s) {
        return s.used && s.seq == frame.seq;
    });

    if (it == slots_.end()) {
        // Квитанція на кадр, який ми вже зняли з обліку: приймач відповів на дублікат.
        ++stats_.stray_ack;
        return;
    }

    it->used = false;
    --in_flight_;
    ++stats_.acked;
}

std::expected<std::uint8_t, Error> Sender::submit(Bytes payload, Millis now) {
    if (payload.size() > kMaxPayload) {
        return std::unexpected(Error::TooLong);
    }

    const auto it = std::ranges::find_if(slots_, [](const Slot& s) { return !s.used; });
    if (it == slots_.end()) {
        return std::unexpected(Error::WindowFull);
    }

    const auto wire = build_frame(next_seq_, payload, it->wire);
    if (!wire) {
        return std::unexpected(wire.error());
    }

    it->used = true;
    it->seq = next_seq_;
    it->len = wire->size();
    it->tries = 1;
    it->deadline = now + kRetryTimeout;

    next_seq_ = static_cast<std::uint8_t>(next_seq_ + 1);
    ++in_flight_;
    ++stats_.sent;

    sink_(*wire);
    return it->seq;
}

std::expected<void, Error> Sender::tick(Millis now) {
    bool link_down = false;

    for (Slot& slot : slots_) {
        if (!slot.used || now < slot.deadline) {
            continue;
        }

        if (slot.tries >= kMaxTries) {
            slot.used = false;
            --in_flight_;
            ++stats_.lost;
            link_down = true;   // далі повторювати немає сенсу: лінія мертва
            continue;
        }

        ++slot.tries;
        slot.deadline = now + kRetryTimeout;
        ++stats_.retrans;
        sink_(Bytes{slot.wire.data(), slot.len});
    }

    if (link_down) {
        return std::unexpected(Error::LinkDown);
    }
    return {};
}

}  // namespace link
