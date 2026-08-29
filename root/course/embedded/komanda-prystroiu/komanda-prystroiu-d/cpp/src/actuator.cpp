#include "actuator.hpp"

#include <algorithm>
#include <format>
#include <iostream>

namespace cmdctl {
namespace {

// Набір перевантажень для std::visit — щоб кожна робота розбиралася своєю
// гілкою, а компілятор ловив забутий варіант.
template <class... Ts>
struct overload : Ts... { using Ts::operator()...; };
template <class... Ts>
overload(Ts...) -> overload<Ts...>;

}  // namespace

void Actuator::set_supply_ok(bool ok) {
    supply_ok_ = ok;
    std::cout << std::format("      [залізо] шина живлення приводів: {}\n", ok ? "у нормі" : "просіла");
}

void Actuator::set_obstacle(std::optional<std::int32_t> position) {
    obstacle_ = position;
    if (position) {
        std::cout << std::format("      [залізо] механічна перешкода на позиції {}\n", *position);
    }
}

std::expected<void, Error> Actuator::start(Type type, std::span<const std::byte> payload) {
    if (busy()) return std::unexpected(Error::UnknownType);   // диспетчер такого не допускає

    switch (type) {
        case Type::Noop:
            // Рух у ту саму точку: завершиться на першому ж poll().
            job_ = Move{position_, position_, clock_.now()};
            return {};

        case Type::SetRelay: {
            if (payload.size() < 2) return std::unexpected(Error::BadPayload);
            const auto channel = std::to_integer<std::uint8_t>(payload[0]);
            const bool on      = std::to_integer<std::uint8_t>(payload[1]) != 0;
            if (channel >= relay_.size()) return std::unexpected(Error::BadPayload);
            // Замкнути ключ при просілій шині — це залипле реле й скид МК.
            if (!supply_ok_) return std::unexpected(Error::SupplySag);

            relay_[channel] = on;
            std::cout << std::format("      [залізо] реле {} -> {}\n", channel, on ? "ON" : "OFF");
            job_ = Move{position_, position_, clock_.now()};   // миттєва робота: завершиться відразу
            return {};
        }

        case Type::GotoPos: {
            const auto target = get_i32(payload);
            if (!target) return std::unexpected(Error::BadPayload);
            if (!supply_ok_) return std::unexpected(Error::SupplySag);

            if (*target != position_) {
                std::cout << std::format("      [залізо] каретка {} -> {} ({} кроків/с)\n",
                                         position_, *target, StepRateHz);
            }
            job_ = Move{position_, *target, clock_.now()};
            return {};
        }

        case Type::DispenseMl: {
            const auto ml = get_u16(payload);
            if (!ml || *ml == 0) return std::unexpected(Error::BadPayload);
            if (!supply_ok_) return std::unexpected(Error::SupplySag);

            std::cout << std::format("      [залізо] насос: наливаємо {} мл\n", *ml);
            job_ = Pour{static_cast<std::int32_t>(*ml), clock_.now()};
            return {};
        }

        case Type::Calibrate:
            std::cout << std::format("      [залізо] калібрування АЦП ({} мс)\n", CalibrateMs.count());
            job_ = Calib{clock_.now()};
            return {};
    }
    return std::unexpected(Error::UnknownType);
}

std::optional<Outcome> Actuator::advance_move(Move& job) {
    const Millis elapsed = clock_.now() - job.started;
    const auto steps = static_cast<std::int64_t>(elapsed.count()) * StepRateHz / 1000;
    const std::int32_t dir = (job.to >= job.from) ? 1 : -1;
    const std::int64_t raw = static_cast<std::int64_t>(job.from) + dir * steps;

    std::int32_t pos = (dir > 0) ? static_cast<std::int32_t>(std::min<std::int64_t>(raw, job.to))
                                 : static_cast<std::int32_t>(std::max<std::int64_t>(raw, job.to));

    // Струмовий захист: перешкода на шляху зупиняє вал раніше цілі.
    if (obstacle_) {
        const bool crossed = (dir > 0) ? (pos >= *obstacle_ && job.from < *obstacle_)
                                       : (pos <= *obstacle_ && job.from > *obstacle_);
        if (crossed) {
            position_ = *obstacle_;
            std::cout << std::format("      [залізо] СТРУМОВИЙ ЗАХИСТ: вал став на {}\n", position_);
            return Outcome{Error::Stall, position_};
        }
    }

    position_ = pos;
    if (pos == job.to) return Outcome{Error::Ok, pos};
    return std::nullopt;
}

std::optional<Outcome> Actuator::advance_pour(Pour& job) {
    const Millis elapsed = clock_.now() - job.started;
    if (!supply_ok_) {
        // Напруга просіла посеред наливання — насос став.
        return Outcome{Error::SupplySag, static_cast<std::int32_t>(elapsed / MsPerMl)};
    }
    if (elapsed >= job.ml * MsPerMl) return Outcome{Error::Ok, job.ml};
    return std::nullopt;
}

std::optional<Outcome> Actuator::advance_calib(Calib& job) {
    if (clock_.now() - job.started >= CalibrateMs) return Outcome{Error::Ok, 37};
    return std::nullopt;
}

std::optional<Outcome> Actuator::poll() {
    auto result = std::visit(overload{
        [](Idle&) -> std::optional<Outcome> { return std::nullopt; },
        [this](Move& job)  { return advance_move(job); },
        [this](Pour& job)  { return advance_pour(job); },
        [this](Calib& job) { return advance_calib(job); },
    }, job_);

    if (result) job_ = Idle{};   // термінальний результат віддається один раз
    return result;
}

void Actuator::abort() {
    if (busy()) {
        std::cout << std::format("      [залізо] АВАРІЙНА ЗУПИНКА: струм із драйвера знято на позиції {}\n",
                                 position_);
    }
    job_ = Idle{};
}

void Actuator::home() {
    std::cout << std::format("      [залізо] гомінг: механізм зводиться в нульову точку з {}\n", position_);
    position_ = 0;
    relay_.fill(false);
    job_ = Idle{};
}

}  // namespace cmdctl
