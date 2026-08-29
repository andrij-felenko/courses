/* Ревізія кремнію: які саме дефекти з Errata Sheet лежать на столі.
 *
 * Партія завжди змішана, тому про ревізію питають сам чип, а не напис на
 * корпусі й не припущення.
 */
#pragma once

#include <cstdint>

namespace usart {

enum class Revision : std::uint16_t {
    unknown = 0x0000, // IDCODE не збігся з очікуваним чипом
    rev_a   = 0x1000, // Rev A — дефект TE описано в Errata
    rev_b   = 0x2000, // Rev B — дефект усунено в кремнії
};

/* Модель чипа, під яку писана прошивка (DEV_ID у DBGMCU_IDCODE [11:0]) */
inline constexpr std::uint16_t expected_device_id = 0x467;

/* DEV_ID із DBGMCU_IDCODE */
[[nodiscard]] std::uint16_t device_id() noexcept;

/* REV_ID із DBGMCU_IDCODE. Для чужого DEV_ID повертає unknown: ревізія
 * іншої моделі до нашого Errata Sheet стосунку не має. */
[[nodiscard]] Revision revision() noexcept;

/* Невідомий кремній трактуємо як дефектний: обхід коштує одну транзакцію
 * читання, а його відсутність — зіпсований перший байт кожної сесії. */
[[nodiscard]] constexpr bool needs_te_workaround(Revision rev) noexcept
{
    return rev != Revision::rev_b;
}

} // namespace usart
