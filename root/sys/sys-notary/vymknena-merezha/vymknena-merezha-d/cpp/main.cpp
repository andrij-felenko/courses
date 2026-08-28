#include <cstdint>
#include <cstddef>
#include <string_view>
#include <chrono>
#include <algorithm>
#include <concepts>

namespace cellular {

using namespace std::chrono_literals;

/* Константи таймінгів та безпеки */
inline constexpr uint32_t kMaxSearchAttempts = 5;
inline constexpr auto kBaseBackoff = 60s;
inline constexpr auto kMaxBackoff = 24h;
inline constexpr auto kSearchTimeout = 45s;
inline constexpr auto kPwrkeyPulse = 1s;

enum class State : uint8_t {
    PoweredDown = 0,
    PoweringOn,
    AtCheck,
    ConfigRat,
    WaitRegistration,
    Connected,
    PoweringOff,
    SleepBackoff
};

enum class RadioAccessTech : uint8_t {
    LteM = 0,
    NbIoT,
    Gsm2G
};

/* Концепт апаратного рівня (HAL) */
template <typename T>
concept ModemHal = requires(T hal, std::string_view cmd, std::string_view resp, std::chrono::milliseconds timeout) {
    { hal.set_power_switch(bool{}) } -> std::same_as<void>;
    { hal.set_pwrkey(bool{}) } -> std::same_as<void>;
    { hal.set_dtr(bool{}) } -> std::same_as<void>;
    { hal.set_uart_pins(bool{}) } -> std::same_as<void>;
    { hal.send_at_command(cmd, resp, timeout) } -> std::same_as<bool>;
    { hal.get_tick_ms() } -> std::same_as<uint32_t>;
    { hal.get_random_jitter(uint32_t{}) } -> std::same_as<uint32_t>;
};

/* Клас безпечного контролера стільникового зв'язку */
template <ModemHal HalType>
class ModemController {
public:
    explicit constexpr ModemController(HalType& hal) noexcept
        : hal_{hal} {}

    void init() noexcept {
        state_ = State::PoweredDown;
        current_rat_ = RadioAccessTech::LteM;
        attempt_count_ = 0;
        hal_.set_power_switch(false);
        hal_.set_uart_pins(false);
    }

    [[nodiscard]] constexpr State state() const noexcept { return state_; }
    [[nodiscard]] constexpr RadioAccessTech current_rat() const noexcept { return current_rat_; }
    [[nodiscard]] constexpr bool is_connected() const noexcept { return state_ == State::Connected; }

    void step() noexcept {
        const uint32_t now_ms = hal_.get_tick_ms();
        const auto elapsed = std::chrono::milliseconds{now_ms - state_enter_time_ms_};

        switch (state_) {
            case State::PoweredDown:
                hal_.set_power_switch(true);
                hal_.set_uart_pins(true);
                transition_to(State::PoweringOn, now_ms);
                break;

            case State::PoweringOn:
                if (elapsed < kPwrkeyPulse) {
                    hal_.set_pwrkey(true);
                } else if (elapsed < (kPwrkeyPulse + 2000ms)) {
                    hal_.set_pwrkey(false);
                } else {
                    transition_to(State::AtCheck, now_ms);
                }
                break;

            case State::AtCheck:
                if (hal_.send_at_command("AT\r\n", "OK", 1000ms)) {
                    hal_.send_at_command("ATE0\r\n", "OK", 500ms);
                    transition_to(State::ConfigRat, now_ms);
                } else if (elapsed > 10s) {
                    transition_to(State::PoweringOff, now_ms);
                }
                break;

            case State::ConfigRat:
                configure_radio_technology();
                hal_.send_at_command("AT+CEREG=2\r\n", "OK", 1000ms);
                hal_.send_at_command("AT+COPS=0\r\n", "OK", 5000ms);
                transition_to(State::WaitRegistration, now_ms);
                break;

            case State::WaitRegistration:
                if (hal_.send_at_command("AT+CEREG?\r\n", "+CEREG: 2,1", 2000ms) ||
                    hal_.send_at_command("AT+CEREG?\r\n", "+CEREG: 2,5", 2000ms)) {
                    attempt_count_ = 0;
                    transition_to(State::Connected, now_ms);
                } else if (elapsed > kSearchTimeout) {
                    rotate_rat_or_backoff(now_ms);
                }
                break;

            case State::Connected:
                /* Сесія активна. Передачу даних координує протокольний стек */
                break;

            case State::PoweringOff:
                hal_.send_at_command("AT+QPOWD=1\r\n", "POWERED DOWN", 3000ms);
                hal_.set_power_switch(false);
                hal_.set_uart_pins(false);
                transition_to(State::SleepBackoff, now_ms);
                break;

            case State::SleepBackoff:
                if (elapsed >= sleep_duration_) {
                    transition_to(State::PoweredDown, now_ms);
                }
                break;
        }
    }

private:
    void transition_to(State new_state, uint32_t now_ms) noexcept {
        state_ = new_state;
        state_enter_time_ms_ = now_ms;
    }

    void configure_radio_technology() noexcept {
        switch (current_rat_) {
            case RadioAccessTech::LteM:
                hal_.send_at_command("AT+QCFG=\"nwscanmode\",3,1\r\n", "OK", 1000ms);
                hal_.send_at_command("AT+QCFG=\"iotopmode\",0,1\r\n", "OK", 1000ms);
                hal_.send_at_command("AT+QCFG=\"band\",0,800080,0,1\r\n", "OK", 1000ms);
                break;
            case RadioAccessTech::NbIoT:
                hal_.send_at_command("AT+QCFG=\"nwscanmode\",3,1\r\n", "OK", 1000ms);
                hal_.send_at_command("AT+QCFG=\"iotopmode\",1,1\r\n", "OK", 1000ms);
                break;
            case RadioAccessTech::Gsm2G:
                hal_.send_at_command("AT+QCFG=\"nwscanmode\",1,1\r\n", "OK", 1000ms);
                break;
        }
    }

    void rotate_rat_or_backoff(uint32_t now_ms) noexcept {
        if (current_rat_ == RadioAccessTech::LteM) {
            current_rat_ = RadioAccessTech::NbIoT;
            transition_to(State::ConfigRat, now_ms);
        } else if (current_rat_ == RadioAccessTech::NbIoT) {
            current_rat_ = RadioAccessTech::Gsm2G;
            transition_to(State::ConfigRat, now_ms);
        } else {
            current_rat_ = RadioAccessTech::LteM;
            attempt_count_++;
            sleep_duration_ = calculate_backoff();
            transition_to(State::PoweringOff, now_ms);
        }
    }

    [[nodiscard]] std::chrono::seconds calculate_backoff() const noexcept {
        const uint32_t shift = std::min(attempt_count_, 10u);
        auto backoff_sec = kBaseBackoff * (1u << shift);
        if (backoff_sec > kMaxBackoff) {
            backoff_sec = std::chrono::duration_cast<std::chrono::seconds>(kMaxBackoff);
        }
        const uint32_t jitter_max = static_cast<uint32_t>(backoff_sec.count() / 5);
        if (jitter_max > 0) {
            backoff_sec += std::chrono::seconds{hal_.get_random_jitter(jitter_max)};
        }
        return backoff_sec;
    }

    HalType& hal_;
    State state_{State::PoweredDown};
    RadioAccessTech current_rat_{RadioAccessTech::LteM};
    uint32_t attempt_count_{0};
    uint32_t state_enter_time_ms_{0};
    std::chrono::seconds sleep_duration_{0s};
};

} // namespace cellular
