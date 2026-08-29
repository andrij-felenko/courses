#pragma once

#include <cstdint>
#include <optional>
#include <string_view>

#include "deny.hpp"
#include "mode.hpp"
#include "params.hpp"
#include "telemetry.hpp"

namespace fm {

/* Сходинка пріоритетів. Число тут не декоративне: воно вирішує, чий запит
   переможе, коли за один такт до автомата приходять і тумблер пілота, і
   аварія живлення. */
enum class Priority : std::uint8_t {
    None          = 0,
    Routine       = 1,  // тумблер RC або MAV_CMD_DO_SET_MODE
    PilotOverride = 2,  // рух стіків скасовує автономію
    NavFailsafe   = 3,  // втрата лінка, геозона, розряд Stage 1
    Critical      = 4,  // Stage 2 живлення, крах оцінювачів
    Hardware      = 5   // апаратна відсічка, парашут
};

[[nodiscard]] std::string_view name(Priority priority) noexcept;

/* Чи має право запит пріоритету request витіснити стан, поставлений
   пріоритетом active. Рівень 3 пілот перехоплює, рівень 4 — уже ні. */
[[nodiscard]] constexpr bool overrides(Priority request, Priority active) noexcept
{
    if (active == Priority::None) {
        return true;
    }
    if (request >= Priority::Hardware) {
        return true;   // апаратну відсічку не перебиває ніщо
    }
    if (active >= Priority::Critical) {
        return false;  // Stage 2 блокує й оператора, і місію
    }
    if (active == Priority::NavFailsafe) {
        // Рівень 3 пілот має право перехопити: якщо пульт знову в ефірі й
        // людина свідомо бере керування, автомат поступається.
        return request >= Priority::Routine;
    }
    return request >= active;
}

struct Preemption {
    Priority         priority{};
    Mode             mode{};
    Severity         severity{};
    std::string_view reason{};
};

namespace failsafe {

/* Арбітр аварій: єдина точка, де народжуються витіснення. Функція чиста — вона
   лише читає стан і повертає рішення, а міняє режим автомат. Порожній
   optional означає «аварії немає», а не «нічого не знайшли». */
[[nodiscard]] std::optional<Preemption> evaluate(const VehicleState& s, const Params& p,
                                                 Mode current, bool inAir);

/* Порушення геозони — окремо, бо ту саму перевірку показує телеметрія. */
[[nodiscard]] bool fenceBreached(const VehicleState& s, const Params& p) noexcept;

}  // namespace failsafe
}  // namespace fm
