#pragma once

// Клієнтський скінченний автомат транзакції «команда — квитанція».
// Монотонний час подається ЗЗОВНІ (аргумент now): так автомат перевіряється
// без реального очікування й однаково працює під RTOS і в наземній станції.

#include "mav_command.h"

#include <chrono>
#include <functional>
#include <string>
#include <variant>

enum class TxState {
    Idle,
    WaitingAck,
    InProgress,
    Success,
    Rejected,
    TimeoutFailure,
};

const char* state_name(TxState s);

struct Outcome {
    TxState      state         = TxState::Idle;
    MavResult    result        = MavResult::Accepted;
    std::int32_t result_param2 = 0;
    unsigned     attempts      = 0;  // скільки кадрів пішло в ефір
    std::string  message;
};

class CommandClient {
public:
    using Clock      = std::chrono::steady_clock;
    using TimePoint  = Clock::time_point;
    using DoneCb     = std::function<void(const Outcome&)>;
    using ProgressCb = std::function<void(std::uint8_t)>;

    CommandClient(ILink& link,
                  std::uint8_t gcs_system    = 255,
                  std::uint8_t gcs_component = 190,
                  std::chrono::milliseconds retry_interval = std::chrono::milliseconds(800),
                  std::uint8_t max_retries = 3);

    // Повертає false, якщо транзакційний канал зайнятий: саме цим значенням
    // інтерфейс оператора блокує кнопку до термінального стану.
    bool send(TimePoint now, CommandLong frame, DoneCb on_done, ProgressCb on_progress = {});
    bool send(TimePoint now, CommandInt frame, DoneCb on_done, ProgressCb on_progress = {});

    // Виклик із приймального тракту на КОЖЕН COMMAND_ACK у потоці.
    void on_ack(TimePoint now, const CommandAck& ack);

    // Виклик у головному циклі: перевіряє таймаут і робить повтор.
    void tick(TimePoint now);

    bool           busy() const { return state_ == TxState::WaitingAck || state_ == TxState::InProgress; }
    TxState        state() const { return state_; }
    const Outcome& last_outcome() const { return last_; }

private:
    void start(TimePoint now, DoneCb on_done, ProgressCb on_progress);
    void transmit();
    void finish(TxState state, MavResult result, std::int32_t param2, std::string message);

    ILink&                          link_;
    const std::uint8_t              gcs_system_;
    const std::uint8_t              gcs_component_;
    const std::chrono::milliseconds retry_interval_;
    const std::uint8_t              max_retries_;

    std::variant<std::monostate, CommandLong, CommandInt> pending_{};
    TxState       state_            = TxState::Idle;
    TimePoint     deadline_{};
    std::uint8_t  retries_          = 0;
    std::uint16_t command_          = 0;
    std::uint8_t  target_system_    = 0;
    std::uint8_t  target_component_ = 0;

    DoneCb     on_done_{};
    ProgressCb on_progress_{};
    Outcome    last_{};
};
