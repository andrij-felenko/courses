#pragma once

#include <cstdint>
#include <optional>
#include <span>
#include <string_view>

#include "at/command.hpp"
#include "at/config.hpp"
#include "at/inplace_function.hpp"
#include "at/line_reader.hpp"
#include "at/ring_buffer.hpp"
#include "at/static_queue.hpp"
#include "at/urc_table.hpp"

namespace at {

class Engine {
public:
    enum class State : std::uint8_t {
        Idle,               // черга порожня
        Send,               // вибірка з черги й передача в UART TX
        WaitPrompt,         // очікування '>' перед сирими даними
        WaitResponse,       // розбір рядків відповіді
        RetryDelay,         // неблокуюча витримка перед повтором
        TimeoutEscalation,  // модуль промовчав — аварійне відновлення
    };

    struct Hooks {
        InplaceFunction<void(std::span<const std::byte>), config::kCallbackStorage> uart_tx;
        InplaceFunction<Millis(), config::kCallbackStorage> tick;
        /* Викликається, коли модуль не відповів kTimeoutEscalationLimit разів
           поспіль: місце для смикання PWRKEY. Може лишатися порожнім. */
        InplaceFunction<void(), config::kCallbackStorage> on_module_stuck{};
    };

    struct Stats {
        std::uint32_t lines_in{0};
        std::uint32_t urc_lines{0};
        std::uint32_t echo_dropped{0};
        std::uint32_t orphan_lines{0};  // відповідь, що спізнилася після таймауту
        std::uint32_t overflows{0};
        std::uint32_t retries{0};
        std::uint32_t timeouts{0};
        std::uint32_t recoveries{0};
    };

    explicit Engine(Hooks hooks) noexcept;

    /* Рушій прив'язаний до власного буфера (LineReader тримає посилання на
       нього), тож ані копіювати, ані переміщувати його не можна. */
    Engine(const Engine&) = delete;
    Engine& operator=(const Engine&) = delete;

    /* Куди націлювати DMA. */
    [[nodiscard]] std::span<std::uint8_t> rx_target() noexcept { return ring_.dma_target(); }

    bool register_urc(std::string_view prefix, UrcHandler handler) noexcept;

    /* Безпечно викликати з URC-колбеку. Відмовляє, якщо черга повна, текст
       не вліз або запрошення замовлено без даних. */
    bool send(Command command) noexcept;

    /* Єдиний неблокуючий крок. cndtr — вміст регістра лічильника DMA. */
    void poll(std::uint16_t cndtr) noexcept;

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] bool busy() const noexcept { return state_ != State::Idle; }
    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

    [[nodiscard]] static std::string_view to_string(State state) noexcept;

private:
    void pump_rx(std::uint16_t head, Millis now) noexcept;
    void on_line(std::string_view line, Millis now) noexcept;
    void run_fsm(std::uint16_t head, Millis now) noexcept;

    void finish(const Result& result) noexcept;
    void schedule_retry(Millis now) noexcept;
    void escalate(std::uint16_t head) noexcept;
    void abort_queue() noexcept;

    [[nodiscard]] bool retries_left() const noexcept;
    [[nodiscard]] bool expired(Millis now, Millis limit) const noexcept;

    Hooks hooks_;
    RingBuffer ring_{};
    LineReader reader_{ring_};
    StaticQueue<Command, config::kQueueCapacity> queue_{};
    UrcTable urc_{};

    State state_{State::Idle};
    std::optional<Command> active_{};
    Millis timer_start_{0};
    StaticString<config::kMaxLine> response_{};

    bool echo_active_{true};   // після живлення модуль у режимі ATE1
    std::uint8_t consecutive_timeouts_{0};

    Stats stats_{};
};

}  // namespace at
