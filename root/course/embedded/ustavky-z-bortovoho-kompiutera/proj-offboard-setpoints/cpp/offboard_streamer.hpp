#pragma once

#include <atomic>
#include <chrono>
#include <cstdint>
#include <mutex>
#include <stop_token>
#include <string>

#include "mavlink_link.hpp"

// Періодичний таймер ядра. Абсолютний: період не «пливе» від тривалості
// тіла циклу, на відміну від sleep_for, який додає свій сон до роботи.
class PeriodicTimer {
public:
    explicit PeriodicTimer(std::chrono::nanoseconds period);
    ~PeriodicTimer();
    PeriodicTimer(const PeriodicTimer&) = delete;
    PeriodicTimer& operator=(const PeriodicTimer&) = delete;

    // Блокується до наступного такту. Повертає кількість тактів, що
    // минули: більше за один означає, що ми проспали.
    std::uint64_t wait();

private:
    int fd_{-1};
};

class OffboardStreamer {
public:
    enum class State {
        Idle,            // порт відкрито, уставок не шлемо
        PreStreaming,    // 16 кадрів нулів, щоб FCU побачив потік
        RequestMode,     // потік не рвемо і просимо режим Offboard
        ActiveStreaming, // трансляція цілей планувальника
        HoldFallback     // планувальник відстав — гальмуємо до нуля
    };

    OffboardStreamer(const std::string& port, speed_t baud,
                     std::uint8_t sys_id, std::uint8_t comp_id);

    // Викликає планувальник зі свого потоку, коли має нову ціль.
    void set_target(const VelocityCommand& cmd);

    void begin_mission();
    void request_shutdown();
    [[nodiscard]] bool running() const noexcept;

    // Тіло RT-потоку: std::jthread{[&](std::stop_token st){ s.run(st); }}.
    void run(std::stop_token stop);

private:
    static constexpr int kStreamHz = 20;
    static constexpr auto kTick = std::chrono::nanoseconds(1'000'000'000 / kStreamHz);
    static constexpr float kTickDt = 1.0f / static_cast<float>(kStreamHz);
    static constexpr std::uint32_t kPreStreamFrames = 16;  // 800 мс потоку
    static constexpr auto kPlannerTimeout = std::chrono::milliseconds(250);
    static constexpr auto kFcuLinkTimeout = std::chrono::seconds(3);
    static constexpr std::uint32_t kHeartbeatDivider = 20;  // раз на секунду
    static constexpr std::uint32_t kModeRetryTicks = 20;
    static constexpr std::uint32_t kModeMaxAttempts = 5;
    static constexpr float kBrakeAccel = 2.0f;  // м/с²: 0.1 м/с за такт
    static constexpr float kZeroSpeedEps = 0.01f;
    static constexpr int kRtPriority = 45;

    void log_tx(const TxResult& result);
    void send_current();
    void brake_step();
    [[nodiscard]] bool stopped() const noexcept;

    MavlinkLink link_;
    PeriodicTimer timer_{kTick};

    State state_{State::Idle};
    VelocityCommand sent_{};  // остання НАДІСЛАНА уставка: база гальмування
    std::uint32_t tick_{0};
    std::uint32_t prestream_count_{0};
    std::uint32_t mode_attempts_{0};
    std::uint32_t mode_tick_{0};
    std::uint32_t late_ticks_{0};
    std::uint32_t tx_errors_{0};
    std::uint32_t rx_drops_{0};

    // Спільний буфер із повільним планувальником. Штамп часу тут
    // головніший за самі числа: без нього ми транслювали б протухлу
    // ціль, поки планувальник лежить під page fault.
    mutable std::mutex mutex_;
    VelocityCommand target_{};
    std::chrono::steady_clock::time_point target_stamp_{};
    bool target_valid_{false};

    std::atomic<bool> running_{true};
    std::atomic<bool> mission_{false};
    std::atomic<bool> shutdown_{false};
};
