#pragma once

#include <expected>

#include "deny.hpp"
#include "mode.hpp"
#include "params.hpp"
#include "telemetry.hpp"

namespace fm {

/* Результат охоронця: або дозвіл без значення, або причина відмови. Тип
   позначено [[nodiscard]] у самій бібліотеці, тож «викликали й забули» тут
   не компілюється мовчки — а саме так і губляться перевірки. */
using GuardResult = std::expected<void, Deny>;

/* Охоронці — чисті функції: жодного запису в стан, жодного побічного ефекту.
   Це не стиль, а вимога атомарності: автомат мусить мати право викликати їх
   у будь-якому порядку й будь-скільки разів, зокрема й задля питання
   «а чи можна повернутися нагору», не змінивши цим нічого. */
namespace guard {

[[nodiscard]] GuardResult imu(const VehicleState& s) noexcept;
[[nodiscard]] GuardResult attitude(const VehicleState& s) noexcept;
[[nodiscard]] GuardResult altitude(const VehicleState& s, const Params& p) noexcept;
[[nodiscard]] GuardResult position(const VehicleState& s, const Params& p) noexcept;
[[nodiscard]] GuardResult guided(const VehicleState& s, const Params& p) noexcept;
[[nodiscard]] GuardResult mission(const VehicleState& s, const Params& p);
[[nodiscard]] GuardResult rtl(const VehicleState& s, const Params& p) noexcept;

/* Диспетчер: охоронець цільового режиму. Невідомий код режиму теж приходить
   сюди — і дістає відмову, а не гілку «нічого не робимо». */
[[nodiscard]] GuardResult check(Mode target, const VehicleState& s, const Params& p);

}  // namespace guard
}  // namespace fm
