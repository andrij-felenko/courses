// load_output.hpp — вихід під навантаження з часом життя.
// Об'єкт існує ⇒ вивід сконфігуровано; об'єкт помер ⇒ навантаження вимкнено.
// Створити «наполовину налаштований» вихід неможливо: конструктор закритий,
// а фабрика повертає або готовий об'єкт, або помилку.
#pragma once

#include "pin.hpp"

#include <expected>
#include <utility>

namespace hw {

enum class Polarity : std::uint8_t {
    ActiveHigh, // навантаження вмикає одиниця
    ActiveLow   // навантаження вмикає нуль (типова релейна плата)
};

template <class PinT, Polarity Pol = Polarity::ActiveHigh>
class LoadOutput {
public:
    [[nodiscard]] static std::expected<LoadOutput, PinFault> create(Speed speed = Speed::Low) noexcept
    {
        // Пасивний рівень у засувку ODR ще до того, як вивід став виходом:
        // у мить перемикання каскад видасть уже правильний рівень.
        driveOff();

        const PinConfig cfg{Mode::Output, OutputType::PushPull, speed, Pull::None};
        if (auto configured = PinT::configure(cfg); !configured) {
            return std::unexpected(configured.error());
        }

        driveOff();
        return LoadOutput{};
    }

    LoadOutput(const LoadOutput&) = delete;
    LoadOutput& operator=(const LoadOutput&) = delete;

    LoadOutput(LoadOutput&& other) noexcept : owns_{std::exchange(other.owns_, false)} {}

    LoadOutput& operator=(LoadOutput&& other) noexcept
    {
        if (this != &other) {
            if (owns_) {
                driveOff();
            }
            owns_ = std::exchange(other.owns_, false);
        }
        return *this;
    }

    ~LoadOutput()
    {
        if (owns_) {
            // Вивід лишається виходом і АКТИВНО тримає пасивний рівень.
            // Hi-Z тут був би гіршим: підвішений затвор зовнішнього ключа
            // відкривається від першої ж наводки.
            driveOff();
        }
    }

    void on() noexcept { PinT::write(Pol == Polarity::ActiveHigh); }
    void off() noexcept { driveOff(); }
    void set(bool state) noexcept { state ? on() : off(); }
    void toggle() noexcept { set(!isOn()); }

    [[nodiscard]] bool isOn() const noexcept
    {
        const bool level = PinT::latched();
        return Pol == Polarity::ActiveHigh ? level : !level;
    }

    // Вмикає навантаження рівно на час області видимості. Ранній return або
    // помилка посеред обробки не лишать реле ввімкненим.
    class Pulse {
    public:
        explicit Pulse(LoadOutput& out) noexcept : out_{out} { out_.on(); }
        Pulse(const Pulse&) = delete;
        Pulse& operator=(const Pulse&) = delete;
        ~Pulse() { out_.off(); }

    private:
        LoadOutput& out_;
    };

    [[nodiscard]] Pulse pulse() noexcept { return Pulse{*this}; }

private:
    LoadOutput() noexcept = default;

    static void driveOff() noexcept { PinT::write(Pol != Polarity::ActiveHigh); }

    bool owns_{true};
};

} // namespace hw
