#pragma once

#include <array>
#include <chrono>
#include <expected>

#include "framing.hpp"

namespace link {

// Передавач із вікном неквитованих кадрів і повторами за таймаутом (Selective Repeat).
class Sender {
public:
    using Millis = std::chrono::milliseconds;

    static constexpr Millis   kRetryTimeout{40};
    static constexpr unsigned kMaxTries = 12;

    struct Stats {
        std::uint32_t sent{};       // нових кадрів
        std::uint32_t retrans{};    // повторів за таймаутом
        std::uint32_t acked{};      // квитанцій, що закрили слот
        std::uint32_t stray_ack{};  // квитанція на вже закритий кадр
        std::uint32_t lost{};       // кадрів, на які вичерпано ліміт спроб
    };

    explicit Sender(ByteSink sink);

    // Читач квитанцій тримає замикання на this — ні копії, ні переміщення.
    Sender(const Sender&) = delete;
    Sender& operator=(const Sender&) = delete;
    Sender(Sender&&) = delete;
    Sender& operator=(Sender&&) = delete;

    // Повертає номер, під яким кадр пішов у лінію.
    [[nodiscard]] std::expected<std::uint8_t, Error> submit(Bytes payload, Millis now);

    void feed_acks(Bytes chunk) { ack_reader_.feed(chunk); }

    // Повтори за таймаутом; LinkDown означає, що ліміт спроб вичерпано.
    [[nodiscard]] std::expected<void, Error> tick(Millis now);

    [[nodiscard]] bool idle() const noexcept { return in_flight_ == 0; }
    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

private:
    struct Slot {
        bool                              used{false};
        std::uint8_t                      seq{0};
        unsigned                          tries{0};
        Millis                            deadline{0};
        std::size_t                       len{0};
        std::array<std::uint8_t, kMaxWire> wire{};   // повтор не перекодовує кадр
    };

    void on_ack(const Frame& frame);

    std::array<Slot, kWindow> slots_{};
    std::uint8_t              next_seq_{0};
    std::size_t               in_flight_{0};

    ByteSink    sink_;
    FrameReader ack_reader_;   // зворотний потік — такі самі кадри
    Stats       stats_{};
};

}  // namespace link
