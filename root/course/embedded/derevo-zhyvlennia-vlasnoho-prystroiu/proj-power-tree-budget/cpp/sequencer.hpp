// sequencer.hpp — кінцевий автомат покрокового вмикання рейок живлення.
//
// Плата підставляється типом-параметром і перевіряється концептом: секвенсер
// не знає ні про регістри, ні про HAL. Помилка повертається через
// std::expected, а не кодом -1, а ключ периферії тримає RAII-об'єкт — доки
// він живий, шина під напругою; його деструктор знімає живлення в правильному
// порядку, і жодна гілка виходу цього не забуде.
#pragma once

#include <chrono>
#include <concepts>
#include <cstdint>
#include <expected>
#include <optional>
#include <string_view>

namespace power {

using Ms = std::chrono::milliseconds;

enum class State : std::uint8_t {
    Off,            // усе знято, шина ізольована
    WaitCorePgood,  // подали EN на перший ступінь
    WaitIoPgood,    // подали DVDD
    ReleaseReset,   // витримка на перехідні процеси, тоді NRST геть
    PeriphRamp,     // ключ відкритий, напруга наростає (dV/dt)
    Ready,
    Fault
};

enum class Error : std::uint8_t {
    InputUndervoltage,  // вхід нижчий за робочий діапазон ще до старту
    CoreTimeout,        // PGOOD першого ступеня не з'явився
    IoTimeout,          // PGOOD шини DVDD не з'явився
    Brownout,           // просідання входу або втрата PGOOD у роботі
    Overcurrent,        // лінія аварії силового ключа
    AlreadyRunning      // старт викликали в польоті
};

[[nodiscard]] constexpr std::string_view to_string(State s) noexcept
{
    switch (s) {
        case State::Off:           return "Off";
        case State::WaitCorePgood: return "WaitCorePgood";
        case State::WaitIoPgood:   return "WaitIoPgood";
        case State::ReleaseReset:  return "ReleaseReset";
        case State::PeriphRamp:    return "PeriphRamp";
        case State::Ready:         return "Ready";
        case State::Fault:         return "Fault";
    }
    return "?";
}

[[nodiscard]] constexpr std::string_view to_string(Error e) noexcept
{
    switch (e) {
        case Error::InputUndervoltage: return "вхід нижчий за робочий діапазон";
        case Error::CoreTimeout:       return "немає PGOOD першого ступеня";
        case Error::IoTimeout:         return "немає PGOOD шини DVDD";
        case Error::Brownout:          return "просідання живлення";
        case Error::Overcurrent:       return "аварія силового ключа";
        case Error::AlreadyRunning:    return "підняття вже триває";
    }
    return "?";
}

struct Config {
    Ms core_pg_timeout{20};   // скільки чекати PGOOD першого ступеня
    Ms io_pg_timeout{20};     // скільки чекати PGOOD DVDD
    Ms reset_release{5};      // витримка перед зняттям NRST
    Ms periph_ramp{8};        // t_r ключа 1…5 мс плюс запас
    std::uint16_t vin_min_mv{9000};  // нижня межа діапазону 9…28 В
};

template <class B>
concept PowerBoard = requires(B board, bool on) {
    { board.core_rail(on) } -> std::same_as<void>;
    { board.io_rail(on) } -> std::same_as<void>;
    { board.periph_switch(on) } -> std::same_as<void>;
    { board.reset_line(on) } -> std::same_as<void>;
    { board.bus_pins(on) } -> std::same_as<void>;
    { board.core_pgood() } -> std::same_as<bool>;
    { board.io_pgood() } -> std::same_as<bool>;
    { board.fault_irq() } -> std::same_as<bool>;
    { board.vin_mv() } -> std::same_as<std::uint16_t>;
};

// Власник живлення периферії. Конструктор відкриває ключ, деструктор спершу
// ізолює сигнальні лінії й лише тоді знімає VCC: доки піни I2C активні,
// датчик без живлення тягне струм витоку через підтяжки та ESD-діоди.
template <PowerBoard B>
class PeripheralRail {
public:
    explicit PeripheralRail(B& board) noexcept : board_{&board}
    {
        board_->bus_pins(false);
        board_->periph_switch(true);
    }

    PeripheralRail(const PeripheralRail&) = delete;
    PeripheralRail& operator=(const PeripheralRail&) = delete;

    ~PeripheralRail()
    {
        board_->bus_pins(false);
        board_->periph_switch(false);
    }

    // Дозволено лише коли напруга на шині вже наросла.
    void attach_bus() noexcept { board_->bus_pins(true); }

private:
    B* board_;
};

template <PowerBoard B>
class Sequencer {
public:
    explicit Sequencer(B& board, Config cfg = {}) noexcept : board_{board}, cfg_{cfg}
    {
        rails_down();
    }

    // Дозволено з Off і Fault: аварія засувна, але не безнадійна.
    std::expected<void, Error> start() noexcept
    {
        if (state_ != State::Off && state_ != State::Fault) {
            return std::unexpected{Error::AlreadyRunning};
        }
        rails_down();

        // Відкривати ключі при просілому вході марно: перетворювач піде
        // в режим прямої передачі й PGOOD не з'явиться взагалі.
        if (board_.vin_mv() < cfg_.vin_min_mv) {
            return fail(Error::InputUndervoltage);
        }

        board_.core_rail(true);
        enter(State::WaitCorePgood);
        return {};
    }

    std::expected<State, Error> tick(Ms elapsed) noexcept
    {
        if (state_ == State::Off || state_ == State::Fault) {
            return state_;
        }
        timer_ += elapsed;

        // Аварія й просідання входу мають пріоритет над кроком послідовності.
        if (board_.fault_irq()) {
            return fail(Error::Overcurrent);
        }
        if (board_.vin_mv() < cfg_.vin_min_mv) {
            return fail(Error::Brownout);
        }

        switch (state_) {
            case State::WaitCorePgood:
                if (board_.core_pgood()) {
                    board_.io_rail(true);
                    enter(State::WaitIoPgood);
                } else if (timer_ >= cfg_.core_pg_timeout) {
                    return fail(Error::CoreTimeout);
                }
                break;

            case State::WaitIoPgood:
                if (board_.io_pgood()) {
                    enter(State::ReleaseReset);
                } else if (timer_ >= cfg_.io_pg_timeout) {
                    return fail(Error::IoTimeout);
                }
                break;

            case State::ReleaseReset:
                // PGOOD спрацьовує на порозі ~90% номіналу: даємо рейці
                // добрати решту й аж тоді відпускаємо NRST.
                if (timer_ >= cfg_.reset_release) {
                    board_.reset_line(false);
                    periph_.emplace(board_);  // ключ відкрито, шина ізольована
                    enter(State::PeriphRamp);
                }
                break;

            case State::PeriphRamp:
                if (timer_ >= cfg_.periph_ramp) {
                    if (!board_.core_pgood() || !board_.io_pgood()) {
                        return fail(Error::Brownout);
                    }
                    periph_->attach_bus();
                    enter(State::Ready);
                }
                break;

            case State::Ready:
                if (!board_.core_pgood() || !board_.io_pgood()) {
                    return fail(Error::Brownout);
                }
                break;

            case State::Off:
            case State::Fault:
                break;
        }
        return state_;
    }

    void shutdown() noexcept
    {
        rails_down();
        enter(State::Off);
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] bool ready() const noexcept { return state_ == State::Ready; }
    [[nodiscard]] unsigned faults() const noexcept { return faults_; }

private:
    void enter(State next) noexcept
    {
        state_ = next;
        timer_ = Ms::zero();
    }

    // Зворотний до підняття порядок; ізоляцію шини й зняття ключа робить
    // деструктор PeripheralRail.
    void rails_down() noexcept
    {
        board_.bus_pins(false);
        periph_.reset();
        board_.reset_line(true);
        board_.io_rail(false);
        board_.core_rail(false);
    }

    std::unexpected<Error> fail(Error err) noexcept
    {
        rails_down();
        enter(State::Fault);
        ++faults_;
        return std::unexpected{err};
    }

    B& board_;
    Config cfg_;
    std::optional<PeripheralRail<B>> periph_{};
    State state_{State::Off};
    Ms timer_{Ms::zero()};
    unsigned faults_{0};
};

}  // namespace power
