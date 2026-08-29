// rs485_port.hpp — напівдуплексний порт RS-485 (C++23).
//
// Той самий автомат, що й у версії на C, але межі власності видно з типів:
// прийнятий кадр віддається як RAII-оренда (поки Frame живий, приймач буфера
// не чіпає), а помилки їдуть у std::expected замість кодів повернення.
#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>

#include "stm32_usart.hpp"

namespace rs485 {

enum class BusError : std::uint8_t {
    Busy,       // шина зайнята або триває пауза розвороту
    TooLong,    // кадр не вміщається в буфер
    Collision,  // відлуння не збіглося з переданим байтом
    NoEcho,     // байти пішли, лінія їх не повернула
    Gap,        // пауза всередині кадру перевищила T1.5
    Overrun,
    Framing,
    Noise
};

// Прапорці статусного регістра, зняті обробником переривання
struct RxFlags {
    bool overrun{};
    bool framing{};
    bool noise{};
};

// Паузи Modbus RTU: понад 19200 біт/с стандарт фіксує абсолютні значення
struct Timing {
    std::chrono::microseconds interChar;  // T1.5
    std::chrono::microseconds frameGap;   // T3.5

    static constexpr Timing forBaud(std::uint32_t baud) noexcept {
        using std::chrono::microseconds;
        if (baud > 19'200) {
            return {microseconds{750}, microseconds{1750}};
        }
        const microseconds symbol{(11'000'000 + baud - 1) / baud};  // 11 біт на символ
        return {symbol * 3 / 2, symbol * 7 / 2};
    }
};

struct Stats {
    std::uint32_t frames{};
    std::uint32_t gaps{};
    std::uint32_t collisions{};
    std::uint32_t overruns{};
    std::uint32_t framings{};
    std::uint32_t noises{};
    std::uint32_t noEcho{};
};

class HalfDuplexPort {
public:
    static constexpr std::size_t kCapacity = 256;

    // Оренда буфера приймача: деструктор повертає буфер драйверу.
    class Frame {
    public:
        Frame(const Frame&) = delete;
        Frame& operator=(const Frame&) = delete;
        Frame(Frame&& other) noexcept : port_{other.port_}, bytes_{other.bytes_} {
            other.port_ = nullptr;
        }
        Frame& operator=(Frame&&) = delete;
        ~Frame() {
            if (port_ != nullptr) {
                port_->releaseFrame();
            }
        }

        [[nodiscard]] std::span<const std::uint8_t> bytes() const noexcept { return bytes_; }

    private:
        friend class HalfDuplexPort;
        Frame(HalfDuplexPort* port, std::span<const std::uint8_t> bytes) noexcept
            : port_{port}, bytes_{bytes} {}

        HalfDuplexPort* port_;
        std::span<const std::uint8_t> bytes_;
    };

    HalfDuplexPort(Stm32Usart& hw, std::uint32_t baud) noexcept;

    HalfDuplexPort(const HalfDuplexPort&) = delete;
    HalfDuplexPort& operator=(const HalfDuplexPort&) = delete;

    std::expected<void, BusError> send(std::span<const std::uint8_t> frame) noexcept;
    [[nodiscard]] std::optional<Frame> receive() noexcept;
    [[nodiscard]] std::optional<BusError> takeError() noexcept;
    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

    // Точки входу з переривань
    void onRxByte(std::uint8_t byte) noexcept;
    void onRxError(RxFlags flags) noexcept;
    void onDmaComplete() noexcept;
    void onTransmissionComplete() noexcept;
    void onTimer() noexcept;

private:
    enum class State : std::uint8_t { Idle, Receiving, Transmitting, Draining, Guard };
    enum class TimerJob : std::uint8_t { None, InterChar, FrameGap, Turnaround };

    void releaseFrame() noexcept;
    void arm(TimerJob job, std::chrono::microseconds delay) noexcept;
    void abortTx(BusError error) noexcept;
    void finishFrame() noexcept;
    bool consumeEcho(std::uint8_t byte) noexcept;

    Stm32Usart& hw_;
    Timing timing_;

    std::array<std::uint8_t, kCapacity> txBuffer_{};
    std::size_t txLength_{0};
    std::size_t echoIndex_{0};
    bool echoPending_{false};

    std::array<std::uint8_t, kCapacity> rxBuffer_{};
    std::size_t rxLength_{0};
    bool rxDiscard_{false};
    bool frameBad_{false};
    bool frameReady_{false};

    State state_{State::Idle};
    TimerJob timerJob_{TimerJob::None};
    std::optional<BusError> lastError_{};
    Stats stats_{};
};

// Єдиний порт плати. ПЕРШИЙ виклик конфігурує периферію — робіть його з main
// до дозволу переривань; далі аргумент швидкості вже не діє.
HalfDuplexPort& bus(std::uint32_t baud = 19'200) noexcept;

}  // namespace rs485
