#include <cstdint>
#include <chrono>
#include <functional>
#include <optional>
#include <string>
#include <iostream>

// Константи результатів MAVLink MAV_RESULT
enum class MavResult : uint8_t {
    Accepted            = 0,
    TemporarilyRejected = 1,
    Denied              = 2,
    Unsupported         = 3,
    Failed              = 4,
    InProgress          = 5,
    Cancelled           = 6,
    CommandLongOnly     = 7,
    CommandIntOnly      = 8
};

// Стан транзакції
enum class TransactionState {
    Idle,
    WaitingAck,
    InProgress,
    Success,
    Rejected,
    TimeoutFailure
};

// Параметри відправки команди
struct CommandRequest {
    uint8_t  target_system{1};
    uint8_t  target_component{1};
    uint16_t command{0};
    float    params[7]{0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
};

// Фінальний підсумок для виклику callback
struct CommandOutcome {
    TransactionState state;
    MavResult        result;
    int32_t          result_param2;
    std::string      message;
};

class MavlinkCommandClient {
public:
    using Clock = std::chrono::steady_clock;
    using Callback = std::function<void(const CommandOutcome&)>;
    using ProgressCallback = std::function<void(uint8_t progress)>;

    MavlinkCommandClient(uint32_t retry_interval_ms = 1000, uint8_t max_retries = 3)
        : retry_interval_(std::chrono::milliseconds(retry_interval_ms))
        , max_retries_(max_retries) {}

    // Ініціалізація відправки команди з блокуванням нового запиту до завершення
    bool send_command(const CommandRequest& req, Callback on_complete, ProgressCallback on_progress = nullptr) {
        if (state_ == TransactionState::WaitingAck || state_ == TransactionState::InProgress) {
            return false; // Канал зайнятий поточною транзакцією
        }

        active_request_ = req;
        on_complete_ = std::move(on_complete);
        on_progress_ = std::move(on_progress);
        
        retry_count_ = 0;
        confirmation_ = 0;
        state_ = TransactionState::WaitingAck;

        transmit_command_long(active_request_, confirmation_);
        deadline_ = Clock::now() + retry_interval_;
        return true;
    }

    // Обробка вхідного пакету COMMAND_ACK від польотного контролера
    void handle_command_ack(uint16_t command, uint8_t result_raw, uint8_t progress, 
                            int32_t result_param2, uint8_t src_sys, uint8_t src_comp) {
        if (state_ != TransactionState::WaitingAck && state_ != TransactionState::InProgress) {
            return; // Немає активної транзакції
        }

        // Перевірка збігу ID команди та адреси відправника
        if (command != active_request_.command || 
            src_sys != active_request_.target_system || 
            src_comp != active_request_.target_component) {
            return; // ACK належить іншому компоненту або фоновому процесу
        }

        auto result = static_cast<MavResult>(result_raw);

        if (result == MavResult::InProgress) {
            state_ = TransactionState::InProgress;
            deadline_ = Clock::now() + retry_interval_; // Продовжуємо таймаут
            if (on_progress_) {
                on_progress_(progress);
            }
            return;
        }

        if (result == MavResult::Accepted) {
            state_ = TransactionState::Success;
            finalize({state_, result, result_param2, "Команду успішно виконано"});
        } else {
            state_ = TransactionState::Rejected;
            finalize({state_, result, result_param2, "Команду відхилено бортом (код: " + std::to_string(result_raw) + ")"});
        }
    }

    // Регулярний виклик у головному циклі програми для перевірки таймаутів
    void tick() {
        if (state_ != TransactionState::WaitingAck && state_ != TransactionState::InProgress) {
            return;
        }

        if (Clock::now() >= deadline_) {
            if (retry_count_ < max_retries_) {
                // Виконуємо повторну відправку
                retry_count_++;
                confirmation_++;
                state_ = TransactionState::WaitingAck;
                
                transmit_command_long(active_request_, confirmation_);
                deadline_ = Clock::now() + retry_interval_;
            } else {
                // Вичерпано всі спроби: фіксуємо тишу
                state_ = TransactionState::TimeoutFailure;
                finalize({state_, MavResult::Failed, -1, "Таймаут: борт не відповів на команду"});
            }
        }
    }

    TransactionState get_state() const { return state_; }

private:
    void transmit_command_long(const CommandRequest& req, uint8_t confirmation) {
        // Тут здійснюється виклик бібліотеки серіалізації:
        // mavlink_msg_command_long_pack(sysid, compid, &msg, req.target_system, 
        //                               req.target_component, req.command, confirmation, ...);
        // uart_write(msg_buffer);
        std::cout << "[TX] COMMAND_LONG cmd=" << req.command 
                  << " target=(" << static_cast<int>(req.target_system) << ":" 
                  << static_cast<int>(req.target_component) << ")"
                  << " conf=" << static_cast<int>(confirmation) 
                  << " try=" << static_cast<int>(retry_count_) << "\n";
    }

    void finalize(CommandOutcome outcome) {
        state_ = outcome.state;
        if (on_complete_) {
            auto cb = std::move(on_complete_);
            on_complete_ = nullptr;
            on_progress_ = nullptr;
            cb(outcome);
        }
        state_ = TransactionState::Idle;
    }

    const std::chrono::milliseconds retry_interval_;
    const uint8_t                   max_retries_;

    TransactionState       state_{TransactionState::Idle};
    CommandRequest         active_request_{};
    Clock::time_point      deadline_{};
    uint8_t                retry_count_{0};
    uint8_t                confirmation_{0};

    Callback               on_complete_{nullptr};
    ProgressCallback       on_progress_{nullptr};
};
