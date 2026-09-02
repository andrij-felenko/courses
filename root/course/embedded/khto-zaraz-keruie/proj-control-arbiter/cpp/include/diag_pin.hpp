#pragma once

#include <chrono>
#include <cstdint>

namespace flight::control {

/* Діагностичний пін під логічний аналізатор. Фронт — момент, коли арбітр
   побачив намір пілота; спад — коли готова уставка пішла в мікшер моторів і
   далі в DShot-кадр. Ширина імпульсу і є затримка реакції диспетчера: при
   400 Гц вона мусить лишатися меншою за один період циклу, 2.5 мс. */
class DiagPin {
public:
    void raise() noexcept;
    void lower() noexcept;

    [[nodiscard]] std::chrono::microseconds last() const noexcept { return last_; }
    [[nodiscard]] std::chrono::microseconds worst() const noexcept { return worst_; }
    [[nodiscard]] std::uint32_t pulses() const noexcept { return pulses_; }

    /* Спад прив'язаний до кінця такту, а виходів із такту може бути кілька.
       Деструктор опустить пін на будь-якому з них — «забути опустити» стає
       неможливо в принципі, і жодних міток на кшталт goto out не треба. */
    class ScopedLow {
    public:
        explicit ScopedLow(DiagPin& pin) noexcept : pin_{pin} {}
        ~ScopedLow() { pin_.lower(); }
        ScopedLow(const ScopedLow&) = delete;
        ScopedLow& operator=(const ScopedLow&) = delete;

    private:
        DiagPin& pin_;
    };

private:
    bool armed_{false};
    std::chrono::steady_clock::time_point rise_{};
    std::chrono::microseconds last_{0};
    std::chrono::microseconds worst_{0};
    std::uint32_t pulses_{0};
};

// Пін на платі один — і об'єкт один.
[[nodiscard]] DiagPin& diag_pin() noexcept;

}  // namespace flight::control
