#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace safety {

using Seconds = std::chrono::duration<float>;

enum class Status : std::uint8_t {
    PassThrough,   // команда планувальника пройшла без змін
    Clamped,       // спроєктовано на допустиму область
    BrakeEngaged,  // керує супервізор: детерміноване сповільнення
    EmergencyStop  // повний нуль на приводи
};

enum class Reason : std::uint8_t {
    None, EmergencyStop, PlannerTimeout, BadPlan, Obstacle,
    Battery, Tilt, SpeedLimit, YawLimit, AccelLimit, SensorLost
};

constexpr std::string_view name(Status s) noexcept
{
    switch (s) {
        case Status::PassThrough:   return "ПРОПУЩЕНО";
        case Status::Clamped:       return "ЗАТИСНУТО";
        case Status::BrakeEngaged:  return "ГАЛЬМУВАННЯ";
        case Status::EmergencyStop: return "АВАР.СТОП";
    }
    return "?";
}

constexpr std::string_view name(Reason r) noexcept
{
    switch (r) {
        case Reason::None:           return "-";
        case Reason::EmergencyStop:  return "кнопка-стоп";
        case Reason::PlannerTimeout: return "сторож-плану";
        case Reason::BadPlan:        return "хибна-уставка";
        case Reason::Obstacle:       return "дистанція";
        case Reason::Battery:        return "напруга";
        case Reason::Tilt:           return "крен";
        case Reason::SpeedLimit:     return "стеля-швидкості";
        case Reason::YawLimit:       return "стеля-рискання";
        case Reason::AccelLimit:     return "темп-розгону";
        case Reason::SensorLost:     return "давач-мовчить";
    }
    return "?";
}

struct Event {
    Seconds       t_begin{};   // початок епізоду
    Seconds       t_end{};     // останній такт епізоду
    Status        status{Status::PassThrough};
    Reason        reason{Reason::None};
    float         value{0.0f}; // значення порушеного інваріанта
    std::uint32_t repeats{0};  // скільки тактів епізод тривав
};

// Кільцевий журнал у статичній памʼяті: запис O(1), жодної алокації.
// Однакові підряд події зливаються в один епізод — інакше 200 записів на секунду
// затерли б буфер за чверть секунди.
template <std::size_t Capacity>
class BlackBox {
    static_assert(Capacity > 0);

public:
    void record(Seconds now, Status st, Reason rs, float value) noexcept
    {
        if (count_ > 0) {
            Event& last = items_[(head_ + Capacity - 1) % Capacity];
            if (last.status == st && last.reason == rs) {
                last.t_end = now;
                last.value = value;
                ++last.repeats;
                return;
            }
        }

        items_[head_] = Event{now, now, st, rs, value, 1};
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        } else {
            ++dropped_; // затерли найстаріший епізод
        }
    }

    [[nodiscard]] std::size_t size() const noexcept { return count_; }
    [[nodiscard]] std::size_t dropped() const noexcept { return dropped_; }

    // Індекс 0 — найстаріший наявний епізод.
    [[nodiscard]] const Event& operator[](std::size_t i) const noexcept
    {
        const std::size_t oldest = (count_ == Capacity)
                                 ? head_
                                 : (head_ + Capacity - count_) % Capacity;
        return items_[(oldest + i) % Capacity];
    }

    // Розгорнути кільце у суцільний відрізок памʼяті виклику — зручно віддавати
    // телеметрії одним шматком. Повертає ту частину dst, яку справді заповнили.
    [[nodiscard]] std::span<Event> snapshot(std::span<Event> dst) const noexcept
    {
        const std::size_t n = std::min(dst.size(), count_);
        for (std::size_t i = 0; i < n; ++i) dst[i] = (*this)[count_ - n + i];
        return dst.first(n);
    }

private:
    std::array<Event, Capacity> items_{};
    std::size_t head_{0};
    std::size_t count_{0};
    std::size_t dropped_{0};
};

} // namespace safety
