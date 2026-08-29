#include "receiver.hpp"

#include <algorithm>

namespace link {

Receiver::Receiver(PayloadHandler on_payload, ByteSink ack_sink)
    : reader_([this](const Frame& frame) { on_frame(frame); }),
      on_payload_(std::move(on_payload)),
      ack_sink_(std::move(ack_sink)) {}

void Receiver::send_ack(std::uint8_t seq) {
    if (!ack_sink_) {
        return;
    }
    std::array<std::uint8_t, kMaxWire> wire{};
    // Квитанція — кадр із порожнім навантаженням, номер несе поле seq.
    if (const auto frame = build_frame(seq, Bytes{}, wire)) {
        ack_sink_(*frame);
    }
}

void Receiver::deliver(std::uint8_t seq, Bytes payload) {
    ++stats_.delivered;
    if (on_payload_) {
        on_payload_(seq, payload);
    }
}

void Receiver::flush() {
    // Щойно дірка в послідовності закрилася, віддаємо всю накопичену пачку
    // строго в порядку зростання номерів.
    for (;;) {
        Slot& slot = slots_[expected_ % kWindow];
        if (!slot.used || slot.seq != expected_) {
            return;
        }
        deliver(slot.seq, Bytes{slot.data.data(), slot.len});
        slot.used = false;
        expected_ = static_cast<std::uint8_t>(expected_ + 1);
    }
}

void Receiver::on_frame(const Frame& frame) {
    // ІНВАРІАНТ КВИТУВАННЯ: ACK шлемо на КОЖЕН цілий кадр, зокрема й на дублікат.
    // Інакше передавач довіку повторюватиме те, що ми давно виконали.
    send_ack(frame.seq);

    const std::uint8_t diff = seq_diff(frame.seq, expected_);

    if (diff == 0) {
        deliver(frame.seq, frame.payload);
        expected_ = static_cast<std::uint8_t>(expected_ + 1);
        flush();
        return;
    }

    if (diff < kWindow) {
        // Кадр випереджає очікуваний: тримаємо його, доки не прийде попередник.
        Slot& slot = slots_[frame.seq % kWindow];
        if (slot.used && slot.seq == frame.seq) {
            ++stats_.duplicates;   // той самий кадр удруге, дані вже в слоті
            return;
        }
        slot.used = true;
        slot.seq = frame.seq;
        slot.len = frame.payload.size();
        std::ranges::copy(frame.payload, slot.data.begin());
        ++stats_.buffered;
        return;
    }

    if (diff >= 128) {
        // Номер позаду очікуваного — це повтор уже виконаної команди.
        ++stats_.duplicates;
        return;
    }

    // Кадр далеко попереду вікна: покласти його нікуди без ризику переплутати
    // зі старим номером після обертання лічильника.
    ++stats_.out_of_window;
}

}  // namespace link
