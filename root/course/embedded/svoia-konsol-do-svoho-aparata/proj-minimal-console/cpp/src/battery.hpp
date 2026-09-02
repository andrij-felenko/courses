#pragma once

#include <chrono>
#include <cstdint>

#include "hal.hpp"

namespace console {

// Кнопка живлення лише відкриває затвор P-канального ключа; далі його тримає
// прошивка. Об'єкт живе рівно стільки, скільки має бути ввімкнене живлення:
// вихід із головної функції будь-якою дорогою гасить пульт.
class PowerLatch {
public:
    [[nodiscard]] bool engage() noexcept
    {
        hal::write(hal::Pin::PowerLatch, true);
        held_ = true;

        // Наростання dV/dt задає RC у колі затвора — тут ми лише чекаємо,
        // поки шина справді підніметься.
        const auto start = hal::hal_millis();
        while (!hal::read(hal::Pin::RailGood)) {
            if (hal::hal_millis() - start > 50u) {
                release();
                return false;   // коротке замикання або зовсім сіла банка
            }
        }
        return true;
    }

    void release() noexcept
    {
        if (held_) {
            hal::write(hal::Pin::PowerLatch, false);
            held_ = false;
        }
    }

    ~PowerLatch() { release(); }

    PowerLatch() = default;
    PowerLatch(const PowerLatch&) = delete;
    PowerLatch& operator=(const PowerLatch&) = delete;

private:
    bool held_{false};
};

class BatteryMonitor {
public:
    enum class Level : std::uint8_t { Ok, Low, Critical };

    // Викликати ЛИШЕ тоді, коли підсилювач потужності вимкнений: під час
    // посилки внутрішній опір банки дає просадку, і фільтр побачить розряд
    // там, де його немає.
    void sample() noexcept
    {
        const std::uint32_t millivolts =
            static_cast<std::uint32_t>(hal::hal_adc_vbat_raw()) * kDividerNum / kDividerDen;

        if (filteredQ8_ == 0) {
            filteredQ8_ = millivolts << 8;   // перший відлік задає початок
        } else {
            // Вага 1/256 при виклику раз на 8 мс — стала часу близько 2 секунд.
            filteredQ8_ += ((millivolts << 8) - filteredQ8_) >> 8;
        }
        updateLevel(filteredQ8_ >> 8);
    }

    [[nodiscard]] std::uint16_t millivolts() const noexcept
    {
        return static_cast<std::uint16_t>(filteredQ8_ >> 8);
    }

    [[nodiscard]] Level level() const noexcept { return level_; }

private:
    // Дільник 100k/100k, опора 3.3 В, дванадцять розрядів.
    static constexpr std::uint32_t kDividerNum = 6600;
    static constexpr std::uint32_t kDividerDen = 4095;

    // Пороги для банки 18650 з гістерезисом 50 мВ: назад у спокійніший стан
    // прошивка переходить лише на 50 мВ вище за поріг спрацювання.
    static constexpr std::uint32_t kLowTrip = 3500;
    static constexpr std::uint32_t kLowClear = 3550;
    static constexpr std::uint32_t kCritTrip = 3300;
    static constexpr std::uint32_t kCritClear = 3350;

    void updateLevel(std::uint32_t millivolts) noexcept
    {
        switch (level_) {
        case Level::Ok:
            if (millivolts < kLowTrip) {
                level_ = Level::Low;
            }
            break;
        case Level::Low:
            if (millivolts < kCritTrip) {
                level_ = Level::Critical;
            } else if (millivolts > kLowClear) {
                level_ = Level::Ok;
            }
            break;
        case Level::Critical:
            if (millivolts > kCritClear) {
                level_ = Level::Low;
            }
            break;
        }
    }

    std::uint32_t filteredQ8_{};
    Level level_{Level::Ok};
};

}   // namespace console
