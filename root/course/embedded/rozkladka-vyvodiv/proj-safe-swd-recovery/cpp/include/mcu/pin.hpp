#pragma once

// Виводи з урахуванням системних ліній. Дві різні дороги до одного порту:
//   Pin::claim<Port, N, Config>() — усе перевірено на етапі компіляції,
//   Pin::configure(...)           — рантайм, помилка приїжджає в std::expected.
// Захоплення PA13/PA14 можливе лише через SwdPinLease, який у деструкторі
// повертає лінії шині налагодження.

#include <cstddef>
#include <cstdint>
#include <expected>
#include <string_view>

namespace mcu {

enum class Port : std::uint8_t { A, B, C, D, E };
enum class Mode : std::uint8_t { Input = 0, Output = 1, Alternate = 2, Analog = 3 };
enum class Pull : std::uint8_t { None = 0, Up = 1, Down = 2 };
enum class Speed : std::uint8_t { Low = 0, Medium = 1, High = 2, VeryHigh = 3 };
enum class OutputType : std::uint8_t { PushPull = 0, OpenDrain = 1 };

enum class PinError : std::uint8_t {
    InvalidPin,        // номер виводу поза 0..15
    InvalidAlternate,  // немає такої альтернативної функції
    SwdPinLocked,      // спроба зайняти PA13/PA14 без ключа
    WrongKey           // хибний ключ оренди
};

struct PinConfig {
    Mode mode{Mode::Input};
    Pull pull{Pull::None};
    Speed speed{Speed::Low};
    OutputType otype{OutputType::PushPull};
    std::uint8_t alternate{0};

    [[nodiscard]] constexpr bool valid() const noexcept
    {
        return alternate < 16 && (mode == Mode::Alternate || alternate == 0);
    }
};

// PA13 (SWDIO) і PA14 (SWCLK). PA15/PB3/PB4 — це JTAG, у чистому SWD вони вільні.
[[nodiscard]] constexpr bool is_swd_pin(Port port, std::uint8_t n) noexcept
{
    return port == Port::A && (n == 13 || n == 14);
}

class SwdPinLease;

class Pin {
public:
    // Компіляційна дорога: вивід SWD або хибний конфіг просто не збереться.
    template <Port P, std::uint8_t N, PinConfig C>
        requires(N < 16 && !is_swd_pin(P, N) && C.valid())
    [[nodiscard]] static Pin claim() noexcept
    {
        apply(P, N, C);
        return Pin{P, N};
    }

    // Рантайм-дорога: номер виводу приходить з таблиці розкладки чи конфігурації плати.
    [[nodiscard]] static std::expected<Pin, PinError> configure(
        Port port, std::uint8_t n, const PinConfig& cfg) noexcept;

    void write(bool level) const noexcept;
    [[nodiscard]] bool read() const noexcept;
    void toggle() const noexcept;

    [[nodiscard]] constexpr Port port() const noexcept { return port_; }
    [[nodiscard]] constexpr std::uint8_t number() const noexcept { return n_; }

private:
    constexpr Pin(Port p, std::uint8_t n) noexcept : port_{p}, n_{n} {}

    static void apply(Port port, std::uint8_t n, const PinConfig& cfg) noexcept;

    Port port_;
    std::uint8_t n_;

    friend class SwdPinLease;
};

inline constexpr std::uint32_t kSwdUnlockKey = 0x5EAF00DU;

// Свідома, оборотна оренда ліній SWD: деструктор повертає PA13/PA14 в AF0.
class SwdPinLease {
public:
    [[nodiscard]] static std::expected<SwdPinLease, PinError> acquire(std::uint32_t key) noexcept;

    SwdPinLease(const SwdPinLease&) = delete;
    SwdPinLease& operator=(const SwdPinLease&) = delete;
    SwdPinLease(SwdPinLease&& other) noexcept;
    SwdPinLease& operator=(SwdPinLease&&) = delete;
    ~SwdPinLease();

    [[nodiscard]] std::expected<Pin, PinError> configure(std::uint8_t n,
                                                         const PinConfig& cfg) noexcept;

private:
    SwdPinLease() noexcept = default;
    bool owns_{true};
};

// Скільки разів обгортка врятувала шину налагодження від захоплення.
[[nodiscard]] std::size_t rejected_count() noexcept;

[[nodiscard]] std::string_view to_string(PinError error) noexcept;

}  // namespace mcu
