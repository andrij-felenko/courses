#pragma once

// Виконавча частина. Поточне завдання — це std::variant активних робіт, а не
// тег плюс купа полів «на всі випадки»: у стані «наливаємо» просто не існує
// поля цільової позиції каретки, і переплутати їх ніде.
//
// start() лише подає струм і повертається; завершення ловить poll() з
// головного циклу. Порожній optional означає «ще в русі» — саме тому фаза 2
// квитування асинхронна.

#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <variant>

#include "clock.hpp"
#include "wire.hpp"

namespace cmdctl {

inline constexpr int StepRateHz     = 400;
inline constexpr Millis MsPerMl     = 100ms;
inline constexpr Millis CalibrateMs = 1500ms;

struct Outcome {
    Error        error{Error::Ok};   // Ok — операція вдалася
    std::int32_t detail{0};          // позиція, налита доза, зміряний зсув
};

class Actuator {
public:
    explicit Actuator(const SimClock& clock) noexcept : clock_{clock} {}

    std::expected<void, Error> start(Type type, std::span<const std::byte> payload);

    // nullopt — робота триває; значення — термінальний результат (віддається раз).
    std::optional<Outcome> poll();

    void abort();
    void home();

    [[nodiscard]] std::int32_t position() const noexcept { return position_; }
    [[nodiscard]] bool busy() const noexcept { return !std::holds_alternative<Idle>(job_); }

    // Керування моделлю заліза для сценаріїв заняття.
    void set_supply_ok(bool ok);
    void set_obstacle(std::optional<std::int32_t> position);

    // Зникнення живлення: драйвер знеструмлено без жодного повідомлення, а
    // механізм фізично лишається там, де його застало скидання.
    void simulate_power_loss() noexcept { job_ = Idle{}; }

private:
    struct Idle {};
    struct Move  { std::int32_t from{}; std::int32_t to{}; Millis started{}; };
    struct Pour  { std::int32_t ml{};   Millis started{}; };
    struct Calib { Millis started{}; };

    std::optional<Outcome> advance_move(Move& job);
    std::optional<Outcome> advance_pour(Pour& job);
    std::optional<Outcome> advance_calib(Calib& job);

    const SimClock& clock_;
    std::variant<Idle, Move, Pour, Calib> job_{Idle{}};
    std::int32_t position_{0};
    std::array<bool, 2> relay_{};
    bool supply_ok_{true};
    std::optional<std::int32_t> obstacle_{};
};

}  // namespace cmdctl
