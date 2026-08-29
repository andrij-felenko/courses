// supervisor.hpp — нагляд за вхідним живленням мовою C++23.
//
// Той самий обов'язок, що й у сішного модуля: вікно UVLO/OVLO з гістерезисом,
// підтвердження аварії кількома вибірками, авто-повтор і засув. Розкладка інша:
// вимірювальний тракт (дільник + фільтр) — окремі значеннєві типи, які можна
// перевіряти на етапі компіляції, а результат нагляду — std::expected: або
// добра напруга, або причина відмови, третього стану не існує.
#pragma once

#include <algorithm>
#include <atomic>
#include <chrono>
#include <compare>
#include <cstdint>
#include <expected>
#include <functional>
#include <limits>
#include <stdexcept>
#include <string_view>

namespace power {

struct Millivolts {
    std::uint32_t value{};
    friend constexpr auto operator<=>(const Millivolts&, const Millivolts&) = default;
};

inline namespace literals {
constexpr Millivolts operator""_mV(unsigned long long v) noexcept
{
    return Millivolts{static_cast<std::uint32_t>(v)};
}
}  // namespace literals

enum class State : std::uint8_t {
    Off,          // ключ розімкнено, чекаємо доброї напруги
    Settling,     // напруга у вікні, витримуємо перед вмиканням
    Running,      // навантаження живиться
    FaultUvlo,
    FaultOvlo,
    FaultEfuse,
    LockedOut     // ліміт повторів вичерпано
};

enum class Fault : std::uint8_t { NotReady, Undervoltage, Overvoltage, EfuseTrip, LockedOut };

std::string_view to_string(State state) noexcept;
std::string_view to_string(Fault fault) noexcept;

// Резистивний дільник разом з АЦП: перерахунок в обидва боки.
class Divider {
public:
    constexpr Divider(std::uint32_t top_ohm, std::uint32_t bottom_ohm,
                      Millivolts vref, std::uint16_t full_scale)
        : top_{top_ohm}, bottom_{bottom_ohm}, vref_{vref}, full_scale_{full_scale}
    {
        if (bottom_ == 0 || full_scale_ == 0 || vref_.value == 0) {
            throw std::invalid_argument{"дільник напруги вироджений"};
        }
    }

    // Код АЦП → напруга шини. Одне ділення на весь перерахунок: розбити його
    // надвоє означало б віддати молодші розряди заокругленню.
    [[nodiscard]] constexpr Millivolts bus(std::uint32_t code) const noexcept
    {
        const std::uint64_t clamped = std::min<std::uint64_t>(code, full_scale_);
        const std::uint64_t num = clamped * vref_.value * (std::uint64_t{top_} + bottom_);
        const std::uint64_t den = std::uint64_t{full_scale_} * bottom_;
        return Millivolts{static_cast<std::uint32_t>(num / den)};
    }

    // Зворотний бік — напруга шини → код. Потрібен стенду, щоб грати роль АЦП.
    [[nodiscard]] constexpr std::uint16_t code(Millivolts bus_mv) const noexcept
    {
        const std::uint64_t num = std::uint64_t{bus_mv.value} * bottom_ * full_scale_;
        const std::uint64_t den = (std::uint64_t{top_} + bottom_) * vref_.value;
        return static_cast<std::uint16_t>(std::min<std::uint64_t>(num / den, full_scale_));
    }

    // Напруга, на якій код упирається в стелю шкали (для дільника 110к/10к — 39.6 В).
    [[nodiscard]] constexpr Millivolts full_scale_bus() const noexcept { return bus(full_scale_); }

private:
    std::uint32_t top_;
    std::uint32_t bottom_;
    Millivolts    vref_;
    std::uint16_t full_scale_;
};

// Експоненційне згладжування у нерухомій комі Q8.
class EmaFilter {
public:
    explicit constexpr EmaFilter(unsigned shift) : shift_{shift}
    {
        if (shift_ > 15) throw std::invalid_argument{"завеликий показник згладжування"};
    }

    // Перша вибірка заряджає фільтр цілком, інакше старт виглядав би просіданням.
    constexpr std::uint32_t operator()(std::uint16_t sample) noexcept
    {
        const std::uint32_t scaled = static_cast<std::uint32_t>(sample) << 8;
        if (!primed_) {
            state_ = scaled;
            primed_ = true;
        } else {
            const auto diff = static_cast<std::int32_t>(scaled) - static_cast<std::int32_t>(state_);
            state_ = static_cast<std::uint32_t>(static_cast<std::int32_t>(state_) + (diff >> shift_));
        }
        return state_ >> 8;
    }

    constexpr void reset() noexcept { state_ = 0; primed_ = false; }

private:
    unsigned      shift_;
    std::uint32_t state_{0};
    bool          primed_{false};
};

// Вікно безпеки: пороги спрацьовування й повернення рознесені гістерезисом.
struct Window {
    Millivolts uvlo_trip{16'500};
    Millivolts uvlo_clear{18'000};
    Millivolts ovlo_clear{30'500};
    Millivolts ovlo_trip{32'000};

    void validate() const;  // кидає std::invalid_argument
};

struct RetryPolicy {
    std::chrono::milliseconds delay{100};   // пауза перед авто-повтором
    std::chrono::milliseconds window{1500}; // тиша такої довжини обнуляє лічильник
    unsigned                  limit{5};     // 0 — повтори без ліміту
};

struct Config {
    Divider     divider;
    Window      window{};
    RetryPolicy retry{};
    unsigned    filter_shift{3};
    unsigned    confirm_samples{5};  // вибірок поспіль, щоб повірити в аварію
    unsigned    settle_samples{20};  // вибірок поспіль у вікні перед пуском
};

struct Stats {
    std::uint64_t samples{0};
    unsigned      uvlo_events{0};
    unsigned      ovlo_events{0};
    unsigned      efuse_events{0};
    unsigned      lockouts{0};
    unsigned      starts{0};
    Millivolts    v_min{std::numeric_limits<std::uint32_t>::max()};
    Millivolts    v_max{0};
};

class Supervisor {
public:
    using SwitchDriver = std::function<void(bool)>;

    Supervisor(Config config, SwitchDriver driver);
    ~Supervisor();  // ключ розмикається разом із наглядачем

    Supervisor(const Supervisor&) = delete;
    Supervisor& operator=(const Supervisor&) = delete;

    void on_sample(std::uint16_t adc_code, std::chrono::milliseconds now);

    // З переривання PIN_FAULT_IRQ: лише прапорець, уся робота — у on_sample.
    void on_efuse_fault() noexcept { efuse_flag_.store(true, std::memory_order_release); }

    // Добра напруга або причина, чому живлення заборонене.
    [[nodiscard]] std::expected<Millivolts, Fault> reading() const noexcept;

    [[nodiscard]] State        state() const noexcept { return state_; }
    [[nodiscard]] Millivolts   voltage() const noexcept { return voltage_; }
    [[nodiscard]] bool         output_enabled() const noexcept { return enabled_; }
    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

    bool clear_lockout(std::chrono::milliseconds now) noexcept;

private:
    void set_output(bool on);
    void enter_fault(State fault, std::chrono::milliseconds now);
    [[nodiscard]] bool inside_window() const noexcept;

    Config       config_;
    SwitchDriver driver_;
    EmaFilter    filter_;

    State state_{State::Off};
    State pending_fault_{State::Off};

    Millivolts voltage_{0};
    bool       enabled_{false};

    unsigned confirm_count_{0};
    unsigned settle_count_{0};
    unsigned retries_used_{0};

    std::chrono::milliseconds retry_at_{0};
    std::chrono::milliseconds last_fault_{0};

    std::atomic<bool> efuse_flag_{false};
    Stats             stats_{};
};

}  // namespace power
