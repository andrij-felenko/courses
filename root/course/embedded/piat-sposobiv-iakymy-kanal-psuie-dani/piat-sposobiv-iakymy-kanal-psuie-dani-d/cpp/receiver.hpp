#pragma once

#include <array>

#include "framing.hpp"

namespace link {

// Стадії 4–5 конвеєра: дедуплікація за порядковим номером, буфер впорядкування
// і диспетчеризація чистого навантаження застосунку.
class Receiver {
public:
    using PayloadHandler = std::function<void(std::uint8_t seq, Bytes payload)>;

    struct Stats {
        std::uint32_t delivered{};      // віддано застосунку
        std::uint32_t duplicates{};     // повтори вже виконаних команд
        std::uint32_t buffered{};       // кадрів, що чекали на попередника
        std::uint32_t out_of_window{};  // номер поза приймальним вікном
    };

    Receiver(PayloadHandler on_payload, ByteSink ack_sink);

    // Читач тримає замикання на this, тож приймач не можна ні копіювати, ні рухати.
    Receiver(const Receiver&) = delete;
    Receiver& operator=(const Receiver&) = delete;
    Receiver(Receiver&&) = delete;
    Receiver& operator=(Receiver&&) = delete;

    // Шматок байтового потоку будь-якого розміру: 1 байт, 3 байти, півтора кадру.
    void feed(Bytes chunk) { reader_.feed(chunk); }

    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }
    [[nodiscard]] const FrameReader::Stats& frame_stats() const noexcept { return reader_.stats(); }
    [[nodiscard]] std::uint8_t expected() const noexcept { return expected_; }

private:
    struct Slot {
        bool                                   used{false};
        std::uint8_t                           seq{0};
        std::size_t                            len{0};
        std::array<std::uint8_t, kMaxPayload>  data{};
    };

    void on_frame(const Frame& frame);
    void deliver(std::uint8_t seq, Bytes payload);
    void flush();
    void send_ack(std::uint8_t seq);

    FrameReader              reader_;
    std::array<Slot, kWindow> slots_{};   // буфер впорядкування, слот = seq % kWindow
    std::uint8_t              expected_{0};

    PayloadHandler on_payload_;
    ByteSink       ack_sink_;
    Stats          stats_{};
};

}  // namespace link
