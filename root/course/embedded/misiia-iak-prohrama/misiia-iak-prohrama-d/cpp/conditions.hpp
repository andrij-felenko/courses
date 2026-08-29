#pragma once

#include <cstdint>
#include <optional>
#include <variant>

#include "geo.hpp"

namespace mission {

/* Лічильник мілісекунд мікроконтролера. Окремий тип саме тому, що
   різницю з ним можна брати ЛИШЕ в беззнаковій арифметиці: сира
   uint32_t про це не нагадує, а переповнення настає кожні 49.7 доби. */
class Millis {
public:
    Millis() = default;
    explicit constexpr Millis(std::uint32_t raw) noexcept : raw_{raw} {}

    [[nodiscard]] constexpr std::uint32_t raw() const noexcept { return raw_; }

    /* Обгортання беззнакового тут не вада, а весь механізм. */
    [[nodiscard]] constexpr std::uint32_t since(Millis earlier) const noexcept
    {
        return raw_ - earlier.raw_;
    }

    [[nodiscard]] constexpr Millis operator+(std::uint32_t ms) const noexcept
    {
        return Millis{raw_ + ms};
    }

private:
    std::uint32_t raw_{0};
};

inline constexpr float kYawToleranceDeg = 2.0F;
inline constexpr float kYawDefaultDps   = 30.0F;

/* Те, що умова бачить щотакту. */
struct ConditionContext {
    Millis   now{};
    GeoPoint position{};
    GeoPoint next_waypoint{};   /* активна ціль навігаційного контуру */
    float    yaw_deg{0.0F};
    float    battery_soc_pct{100.0F};
};

/* Кожна CONDITION-команда MAVLink — власний тип. Диспетчер працює
   через std::visit, тож жодного switch за тегом у коді не лишається. */
struct Delay {
    Millis        started{};
    std::uint32_t duration_ms{0};
};

struct Distance {
    float trigger_m{0.0F};
};

struct Yaw {
    Millis started{};
    float  start_deg{0.0F};
    float  target_deg{0.0F};
    float  rate_dps{kYawDefaultDps};
};

using Condition = std::variant<Delay, Distance, Yaw>;

[[nodiscard]] Condition make_delay(float seconds, const ConditionContext& ctx) noexcept;
[[nodiscard]] Condition make_distance(float metres) noexcept;
[[nodiscard]] Condition make_yaw(float target_deg, float rate_dps,
                                 const ConditionContext& ctx) noexcept;

[[nodiscard]] bool is_met(const Condition& c, const ConditionContext& ctx) noexcept;

/* Проміжна уставка курсу для CONDITION_YAW; для решти умов — nullopt,
   і контур навігації сам вибирає курс на ціль. */
[[nodiscard]] std::optional<float> yaw_setpoint(const Condition& c,
                                                const ConditionContext& ctx) noexcept;

/* Однополюсний НЧ-фільтр напруги АКБ: під ривком тяги напруга
   просідає на внутрішньому опорі, і сире порівняння дає хибні
   спрацьовування. Постійна часу 2–5 с гасить ці провали. */
class BatteryFilter {
public:
    explicit BatteryFilter(float tau_s = 3.0F) noexcept
        : tau_s_{tau_s > 0.0F ? tau_s : 3.0F} {}

    float update(float raw_v, float dt_s) noexcept;

    [[nodiscard]] std::optional<float> value() const noexcept
    {
        return primed_ ? std::optional<float>{value_v_} : std::nullopt;
    }

private:
    float value_v_{0.0F};
    float tau_s_{3.0F};
    bool  primed_{false};
};

}  // namespace mission
