// scanner.hpp — прохід простору адрес і звіт про нього.
// Сканер не знає ні про HAL, ні про друк: усе, чого він хоче від шини,
// записано в концепті Master.
#pragma once

#include "i2c/address.hpp"

#include <bitset>
#include <concepts>
#include <cstddef>
#include <ranges>

namespace i2c {

enum class Probe : std::uint8_t {
    ack,   // ведений притиснув SDA на 9-му такті
    nack,  // тиша: за цією адресою нікого немає
    busy,  // лінія не звільняється — схоже на залипання SDA
    error, // BERR/ARLO: електричний збій усередині кадру
};

template <class M>
concept Master = requires(M& master, Address addr) {
    { master.probe(addr) } -> std::same_as<Probe>;
    { master.busy() } -> std::same_as<bool>;
    { master.settle() } -> std::same_as<void>;
};

class Report {
  public:
    void mark(Address addr, Probe result) noexcept
    {
        ++probed_;
        if (result == Probe::ack) {
            acked_.set(addr.value());
        } else if (result == Probe::error) {
            ++errors_;
        }
    }

    void stall() noexcept { stuck_ = true; }

    [[nodiscard]] bool bus_stuck() const noexcept { return stuck_; }
    [[nodiscard]] std::size_t probed() const noexcept { return probed_; }
    [[nodiscard]] std::size_t errors() const noexcept { return errors_; }
    [[nodiscard]] std::size_t count() const noexcept { return acked_.count(); }

    // Замкнена на землю SDA підтверджує ACK на КОЖНІЙ адресі: десятки
    // «знайдених» пристроїв означають коротке замикання, а не багату плату.
    [[nodiscard]] bool looks_fake() const noexcept { return count() > kSaneDevices; }

    // Лінива послідовність знайдених адрес — без купи й без копії таблиці.
    [[nodiscard]] auto found() const
    {
        return std::views::iota(int{kFirstAddr}, int{kLastAddr} + 1)
             | std::views::filter([this](int v) {
                   return acked_.test(static_cast<std::size_t>(v));
               })
             | std::views::transform([](int v) {
                   return *Address::from_7bit(static_cast<std::uint8_t>(v));
               });
    }

  private:
    static constexpr std::size_t kSaneDevices = 8;

    std::bitset<128> acked_{};
    std::size_t probed_{};
    std::size_t errors_{};
    bool stuck_{};
};

// Стільки збоїв поспіль — і далі стукати немає сенсу.
inline constexpr unsigned kErrorStreakLimit = 4;

template <Master M>
[[nodiscard]] Report scan(M& master)
{
    Report report;

    // Шина зайнята ще до першого START: ведений тримає SDA в нулі.
    if (master.busy()) {
        report.stall();
        return report;
    }

    unsigned streak = 0;
    for (int v = kFirstAddr; v <= int{kLastAddr}; ++v) {
        const Address addr = *Address::from_7bit(static_cast<std::uint8_t>(v));
        const Probe result = master.probe(addr);
        report.mark(addr, result);

        if (result == Probe::busy) {
            report.stall();
            break;
        }
        streak = (result == Probe::error) ? streak + 1 : 0;
        if (streak >= kErrorStreakLimit) {
            report.stall();
            break;
        }

        master.settle(); // слабка підтяжка піднімає лінію не миттєво
    }
    return report;
}

} // namespace i2c
