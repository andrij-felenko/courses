#pragma once

// Модель другого боку каналу: борт із перевірками безпеки й кешем дедуплікації
// та радіоканал із затримкою, втратами й буфером модема скінченної глибини.

#include "mav_command.h"

#include <chrono>
#include <cstddef>
#include <deque>
#include <optional>
#include <variant>

class CommandClient;

namespace copter_mode {
inline constexpr std::int32_t Stabilize = 0;
inline constexpr std::int32_t Auto      = 3;
inline constexpr std::int32_t Guided    = 4;
inline constexpr std::int32_t Rtl       = 6;
}  // namespace copter_mode

const char* mode_name(std::int32_t mode);

// Коди причини у полі result_param2 нашої прошивки.
namespace deny_reason {
inline constexpr std::int32_t NoGpsFix    = 1;
inline constexpr std::int32_t ArmedInAir  = 2;
inline constexpr std::int32_t EkfNotReady = 3;
}  // namespace deny_reason

class SimAutopilot {
public:
    using Clock     = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    // Вікно транзакції: повтор пізніше вважається новим наказом.
    static constexpr std::chrono::milliseconds kTxWindow{3000};

    SimAutopilot(std::uint8_t system_id = 1, std::uint8_t component_id = 1)
        : system_id_(system_id), component_id_(component_id) {}

    // Важелі сценарію заняття.
    void set_gps_fix(bool on)   { gps_fix_ = on; }
    void set_ekf_ready(bool on) { ekf_ready_ = on; }
    void set_dedup(bool on)     { dedup_ = on; }
    void set_powered(bool on)   { powered_ = on; }

    bool         armed() const              { return armed_; }
    bool         in_air() const             { return in_air_; }
    std::int32_t mode() const               { return mode_; }
    bool         gripper_closed() const     { return gripper_closed_; }
    int          gripper_actuations() const { return gripper_actuations_; }
    int          photos() const             { return photos_; }

    // std::nullopt означає тишу: борт знеструмлено, завис або кадр не йому.
    std::optional<CommandAck> handle(TimePoint now, const CommandLong& frame);
    std::optional<CommandAck> handle(TimePoint now, const CommandInt& frame);

    // Проміжні звіти довгої операції, що дозріли на цей момент часу.
    std::optional<CommandAck> poll(TimePoint now);

private:
    bool addressed_to_us(std::uint8_t sys, std::uint8_t comp) const;
    CommandAck execute(TimePoint now, const CommandLong& frame);
    CommandAck execute(const CommandInt& frame);

    template <class Frame>
    CommandAck make_ack(const Frame& frame, MavResult result,
                        std::int32_t param2 = 0, std::uint8_t progress = 255) const {
        CommandAck ack;
        ack.command          = frame.command;
        ack.result           = result;
        ack.progress         = progress;
        ack.result_param2    = param2;
        ack.target_system    = frame.src_system;
        ack.target_component = frame.src_component;
        ack.src_system       = system_id_;
        ack.src_component    = component_id_;
        return ack;
    }

    // Кеш останньої транзакції — той самий, що в бортових стеках.
    struct LastCommandCache {
        bool          valid             = false;
        std::uint8_t  target_system     = 0;
        std::uint8_t  target_component  = 0;
        std::uint16_t command           = 0;
        std::uint8_t  last_confirmation = 0;
        MavResult     result            = MavResult::Accepted;
        std::int32_t  result_param2     = 0;
        TimePoint     stamp{};
    };

    struct TimedAck {
        TimePoint  due;
        CommandAck ack;
    };

    const std::uint8_t system_id_;
    const std::uint8_t component_id_;

    bool         powered_   = true;
    bool         gps_fix_   = false;
    bool         ekf_ready_ = true;
    bool         dedup_     = true;

    bool         armed_              = false;
    bool         in_air_             = false;
    std::int32_t mode_               = copter_mode::Stabilize;
    bool         gripper_closed_     = false;
    int          gripper_actuations_ = 0;
    int          photos_             = 0;
    std::int32_t loiter_lat_         = 0;
    std::int32_t loiter_lon_         = 0;
    float        loiter_alt_         = 0;

    LastCommandCache      cache_{};
    std::deque<TimedAck>  reports_;
};

// Напівдуплексний радіоканал: слот угору, обробка на борту, слот униз.
class SimRadio : public ILink {
public:
    using Clock     = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    // Глибина черги кадрів у модемі; далі буфер UART переповнюється.
    static constexpr std::size_t kModemQueueDepth = 4;

    SimRadio(SimAutopilot& vehicle,
             std::chrono::milliseconds uplink_delay,
             std::chrono::milliseconds downlink_delay)
        : vehicle_(vehicle), uplink_delay_(uplink_delay), downlink_delay_(downlink_delay) {}

    void attach(CommandClient& client) { client_ = &client; }
    void drop_next_uplink(int frames)   { drop_up_ = frames; }
    void drop_next_downlink(int frames) { drop_down_ = frames; }

    void send(const CommandLong& frame) override;
    void send(const CommandInt& frame) override;

    // Головний цикл кличе радіо ПЕРШИМ: воно й приносить сюди поточний час.
    void tick(TimePoint now);

private:
    void enqueue_uplink(std::variant<CommandLong, CommandInt> frame);
    void enqueue_downlink(const CommandAck& ack);

    struct UpFrame {
        TimePoint                              due;
        std::variant<CommandLong, CommandInt>  frame;
    };
    struct DownFrame {
        TimePoint  due;
        CommandAck ack;
    };

    SimAutopilot&                   vehicle_;
    CommandClient*                  client_ = nullptr;
    const std::chrono::milliseconds uplink_delay_;
    const std::chrono::milliseconds downlink_delay_;

    std::deque<UpFrame>   up_;
    std::deque<DownFrame> down_;
    TimePoint             now_ = Clock::now();
    int                   drop_up_   = 0;
    int                   drop_down_ = 0;
};
