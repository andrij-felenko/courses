#pragma once

// Диспетчер команд: кільце ідемпотентності, черга виконання, автомат станів
// і двофазне квитування. Уся пам'ять статична — купи в прошивці немає.

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>

#include "actuator.hpp"
#include "clock.hpp"
#include "journal.hpp"
#include "wire.hpp"

namespace cmdctl {

// Куди йдуть квитанції. Абстрактний інтерфейс, а не std::function: віртуальний
// виклик нічого не розміщує в купі, а std::function — може.
struct AckSink {
    virtual ~AckSink() = default;
    virtual void send(std::span<const std::byte> frame) = 0;
};

class Dispatcher {
public:
    static constexpr std::size_t RingSize  = 16;   // вікно повторів мережі
    static constexpr std::size_t QueueSize = 8;    // глибина черги (залп після сну)

    Dispatcher(const SimClock& clock, Actuator& actuator, Journal& journal, AckSink& sink) noexcept
        : clock_{clock}, actuator_{actuator}, journal_{journal}, sink_{sink} {}

    // Перевірка журналу FRAM при старті прошивки.
    void recover_after_reset();

    // Прийом кадру з радіоканалу.
    std::expected<void, Error> on_frame(std::span<const std::byte> bytes);

    // Крок автомата з головного циклу.
    void tick();

    // Модель зникнення живлення: SRAM обнуляється, деструктори НЕ виконуються,
    // тож відкритий запис у FRAM лишається відкритим — саме на це й розрахована
    // процедура відновлення. Лічильники сценарію збережено для підсумку.
    void simulate_power_loss();

    void print_stats() const;

private:
    struct Record {
        std::uint64_t token{0};
        Type          type{Type::Noop};
        State         state{State::Free};
        std::array<std::byte, MaxPayload> payload{};
        std::uint8_t  payload_len{0};
        Millis        received{0};
        Millis        deadline{0};
        Error         result{Error::Ok};
        std::int32_t  detail{0};

        [[nodiscard]] std::span<const std::byte> data() const noexcept {
            return std::span{payload}.first(payload_len);
        }
        [[nodiscard]] bool pending() const noexcept {
            return state == State::Accepted || state == State::Executing;
        }
    };

    [[nodiscard]] Record* find(std::uint64_t token) noexcept;
    [[nodiscard]] std::optional<std::size_t> allocate() noexcept;
    [[nodiscard]] bool superseded_later(const Record& record) const noexcept;

    bool queue_push(std::size_t slot) noexcept;
    std::optional<std::size_t> queue_pop() noexcept;

    void emit(std::uint8_t phase, const Record& record);
    void finish(Record& record, State state, Error result, std::int32_t detail);

    const SimClock& clock_;
    Actuator&       actuator_;
    Journal&        journal_;
    AckSink&        sink_;

    std::array<Record, RingSize> ring_{};
    std::size_t head_{0};

    std::array<std::size_t, QueueSize> queue_{};
    std::size_t queue_head_{0};
    std::size_t queue_count_{0};

    std::uint32_t last_seq_{0};
    std::optional<std::size_t> active_{};
    std::optional<Journal::Transaction> transaction_{};

    struct Stats {
        std::uint32_t executed{0};
        std::uint32_t duplicates{0};
        std::uint32_t expired{0};
        std::uint32_t superseded{0};
        std::uint32_t replays{0};
        std::uint32_t dropped{0};
    } stats_{};
};

}  // namespace cmdctl
