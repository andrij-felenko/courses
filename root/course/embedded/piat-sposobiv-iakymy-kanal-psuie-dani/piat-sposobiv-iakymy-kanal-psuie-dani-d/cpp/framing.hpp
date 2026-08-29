#pragma once

#include <array>
#include <cstdint>
#include <expected>

#include "link.hpp"

namespace link {

// Кадр, що пройшов усі три перевірки нижнього рівня. Навантаження — вид на
// внутрішній буфер читача: воно живе рівно доти, доки триває виклик обробника.
struct Frame {
    std::uint8_t seq;
    Bytes        payload;
};

// Пакування кадру у виданий буфер; повертає вид на готові до відправки байти.
[[nodiscard]] std::expected<Bytes, Error> build_frame(
    std::uint8_t seq, Bytes payload, std::span<std::uint8_t> wire) noexcept;

// Стадії 1–3 конвеєра: демаркація меж по 0x00, COBS-декодування, контроль CRC-16.
class FrameReader {
public:
    using FrameHandler = std::function<void(const Frame&)>;

    struct Stats {
        std::uint32_t frames{};      // кадрів, що пройшли CRC
        std::uint32_t cobs_errors{}; // структурно пошкоджених тіл
        std::uint32_t crc_errors{};  // кадрів, побитих шумом
        std::uint32_t overflows{};   // випадків, коли роздільник так і не прийшов
    };

    explicit FrameReader(FrameHandler on_frame) : on_frame_(std::move(on_frame)) {}

    // Байти приходять із UART/DMA довільними шматками — і по одному, і пачками.
    void feed(Bytes chunk);

    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

private:
    void feed_byte(std::uint8_t byte);
    void finish_frame();

    std::array<std::uint8_t, kMaxWire>  raw_{};
    std::size_t                         raw_len_{0};
    std::array<std::uint8_t, kMaxFrame> frame_{};
    bool                                desync_{false};   // у лінії сміття, чекаємо 0x00

    FrameHandler on_frame_;
    Stats        stats_{};
};

}  // namespace link
