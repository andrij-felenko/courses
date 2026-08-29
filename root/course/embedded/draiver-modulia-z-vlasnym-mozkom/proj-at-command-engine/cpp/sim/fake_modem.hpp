#pragma once

#include <cstddef>
#include <cstdint>
#include <deque>
#include <span>
#include <string>
#include <string_view>

#include "at/config.hpp"

namespace sim {

/* Симулятор смарт-модуля з боку дроту.

   Потрібен, щоб рушій можна було ганяти без заліза, і навмисно поводиться так
   само паскудно, як справжній модем: віддає луну, розриває довгу відповідь на
   два кадри, з першого разу відповідає "+CME ERROR: 14", вимагає запрошення
   '>' перед сирими даними й іноді мовчить зовсім.

   Це хостовий код, тож тут std::string і std::deque доречні — на відміну від
   самого рушія, який до купи не торкається. */
class FakeModem {
public:
    explicit FakeModem(std::span<std::uint8_t> dma_target) noexcept : dma_{dma_target} {}

    /* Скільки байтів DMA ще НЕ передав — саме це лежить у DMA_CNDTR. */
    [[nodiscard]] std::uint16_t cndtr() const noexcept
    {
        return static_cast<std::uint16_t>(at::config::kRxSize - head_);
    }

    /* Перехоплення передачі: сюди приходить усе, що рушій пише в UART TX. */
    void on_tx(std::span<const std::byte> data, at::Millis now);

    /* Крок часу: віддає в «ефір» те, чому настав час. */
    void tick(at::Millis now);

private:
    struct Pending {
        std::string text;
        std::size_t sent{0};
        std::size_t chunk{0};      // 0 — віддати цілком
        at::Millis gap{0};         // пауза між шматками
        at::Millis due{0};
    };

    void schedule(std::string text, at::Millis due, std::size_t chunk = 0,
                  at::Millis gap = at::Millis{0});
    void emit(std::string_view bytes) noexcept;
    void on_command(at::Millis now);

    std::span<std::uint8_t> dma_;
    std::uint16_t head_{0};
    std::deque<Pending> outbox_{};

    std::string rx_line_{};

    bool echo_{true};              // після живлення модуль у режимі ATE1
    int cfun_attempts_{0};

    bool await_payload_{false};
    std::size_t payload_expect_{0};
    std::size_t payload_got_{0};

    bool urc_closed_done_{false};
    bool urc_ring_done_{false};
};

}  // namespace sim
